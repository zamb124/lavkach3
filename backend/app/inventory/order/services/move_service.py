import logging
import logging
import traceback
import typing
from collections import defaultdict
from optparse import Option

from typing import Any, Optional, List

from sqlalchemy import select, Row
from starlette.requests import Request
from uuid import UUID

from app.inventory.estatus import estatus
from app.inventory.location.enums import VirtualLocationZones, PhysicalLocationClass, LocationClass
from app.inventory.order import OrderType
from app.inventory.order.enums.exceptions_move_enums import MoveErrors
from app.inventory.order.enums.order_enum import OrderStatus, SuggestStatus, TYPE_MAP, OrderClass
from app.inventory.order.models.order_models import Move, MoveType, Order, MoveStatus, \
    SuggestType
from app.inventory.order.schemas.move_schemas import MoveCreateScheme, MoveUpdateScheme, MoveFilter
from app.inventory.quant import Quant
from app.inventory.schemas import CreateMovements, Product
from app.inventory.utills import compare_lists
from core.exceptions.module import ModuleException
# from app.inventory.order.services.move_tkq import move_set_done
from core.helpers.broker import list_brocker
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType, Model

if typing.TYPE_CHECKING:
    from app.inventory.location.models import Location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoveService(BaseService[Move, MoveCreateScheme, MoveUpdateScheme, MoveFilter]):
    """
    Сервис для работы с Мувами
    Мув нельзя создать, если запаса недостаточно (это прям правило)
    Путь мува такоф:
        CREATED: str = 'created'       # Мув создан, но не подтвержден
        CONFIRMING: str = 'confirming' # Мув в процессе утверждения, кванты еще не зарезервированы, резервируются
        CONFIRMED: str = 'confirmed'   # Мув пдтвержден и нужные кванты найдены и зарезервированы
        WAITING: str = 'waiting'       # Ожидает назначения оператора
        ASSIGNED: str = 'assigned'     # Оператор найден и назначен
        PROCESSING: str = 'processing' # Оператор начал действия
        COMPLETING: str = 'completing' # Завершение ордера
        DONE: str = 'done'             # Оператор завершил действия
        CANCELING: str = 'canceled'    # Отменяется, кванты при этом разрезерируются
        CANCELED: str = 'canceled'     # Отменен, кванты при этом разрезерируются
    Порядок вызова методов
    - Создание мува - - -- > CREATED
    - Подтверждение мува - confirm CONFIRMING -- > CONFIRMED (поиск квантов и резервирование запаса def confirm, def set_reserve)
    - Перевод в ожидание - CONFIRMED -- > WAITING (создание саджестов def create_suggests)
    - Назначение пользователя - WAITING -- > ASSIGNED (def set_user)
    - Начало выполнения - ASSIGNED -- > PROCESSING (def set_processing)
    - Завершение выполнения - PROCESSING -- > COMPLETING (def set_done)
    - Перевод в статус DONE - COMPLETING -- > DONE (def set_done)
    - Отменение - - -- > CANCELING -- > CANCELED (def cancel)
    """

    def __init__(self, request: Request):
        super(MoveService, self).__init__(request, Move, MoveCreateScheme, MoveUpdateScheme)

    @permit('move_update')
    async def update(self, id: Any, obj: UpdateSchemaType, commit: bool = True) -> Optional[ModelType]:
        return await super(MoveService, self).update(id, obj, commit)

    @permit('move_list')
    async def list(self, _filter: FilterSchemaType | dict, size: int = 100):
        return await super(MoveService, self).list(_filter, size)

    @list_brocker.task(queue_name='model')
    async def create_suggests(self, move_ids: List, user_id: str):
        """
            Создаются саджесты в зависимости от OrderType и Product
        """
        self = self or list_brocker.state.data['env'].get_env()['move'].service
        suggest_model = self.env['suggest'].model
        location_service = self.env['location'].service
        orders_to_notify = []
        for move_id in move_ids:
            move = await self.get(move_id)
            to_session_add = []
            if move.suggest_list_rel:
                raise ModuleException(status_code=406, enum=MoveErrors.SUGGESTS_ALREADY_CREATED)
            if move.type == MoveType.PRODUCT:
                """Если это перемещение товара из виртуальцой локации, то идентификация локации не нужна"""
                location_src = await location_service.get(move.location_src_id)
                location_dest = await location_service.get(move.location_dest_id)
                if not location_src.location_class in VirtualLocationZones:
                    in_location_suggest_src = suggest_model(**{
                        "move_id": move.id,
                        "priority": 1,
                        "type": SuggestType.IN_LOCATION_SRC,
                        "value": f'{location_src.id}',
                        "company_id": move.company_id,
                        # "user_id": self.user.user_id
                    })
                    to_session_add.append(in_location_suggest_src)
                """Ввод Партии"""  # TODO:  пока хз как праильное
                """Далее саджест на идентификацию товара"""
                in_product_suggest = suggest_model(**{
                    "move_id": move.id,
                    "priority": 2,
                    "type": SuggestType.IN_PRODUCT,
                    "value": f'{move.product_id}',
                    "company_id": move.company_id,
                    # "user_id": self.user.user_id
                })
                to_session_add.append(in_product_suggest)
                """Далее саджест ввода количества"""
                in_quantity_suggest = suggest_model(**{
                    "move_id": move.id,
                    "priority": 3,
                    "type": SuggestType.IN_QUANTITY,
                    "value": f'{move.quantity}',
                    "company_id": move.company_id,
                    # "user_id": self.user.user_id
                })
                to_session_add.append(in_quantity_suggest)
                """Далее саджест на ввод срока годности"""  # TODO:  пока хз как праильное
                """Далее саджест идентификации локации назначения"""
                in_location_suggest_dest = suggest_model(**{
                    "move_id": move.id,
                    "priority": 4,
                    "type": SuggestType.IN_LOCATION_DEST,
                    "value": f'{location_dest.id}',
                    "company_id": move.company_id,
                    # "user_id": self.user.user_id
                })
                to_session_add.append(in_location_suggest_dest)
                move.status = MoveStatus.PROCESSING
                order = await self.env['order'].service.get(move.order_id)
                order.status = OrderStatus.PROCESSING
                self.session.add(order)
                self.session.add(move)
                for suggests_obj in to_session_add:
                    self.session.add(suggests_obj)
            try:
                await self.session.commit()
                await self.session.refresh(move)
            except Exception as ex:
                self.session.rollback()
                raise ex
            await move.notify('update')
            orders_to_notify.append(move.order_id)
        orders = await self.env['order'].service.list({'id__in': orders_to_notify})
        for order in orders:
            await order.notify('update')
            # Итого простой кейс, отсканировал локацию-источник, отсканировал товар, отсканировал локацию-назначения

    @permit('move_user_assign')
    async def user_assign(self, move_id: UUID, user_id: UUID):
        """
            Если прикрепился пользователь, то значит, что необходимо создать саджесты для выполнения
        """
        move = await self.get(move_id)
        # await move.create_suggests()
        move.user_id = user_id
        await self.session.commit()
        return move

    @list_brocker.task(queue_name='model')
    async def confirm(self, move_ids: List[UUID], user_id: str, order_id: Optional[UUID] = None):
        self = self or list_brocker.state.data['env'].get_env()['move'].service
        try:
            await self._moves_confirm(move_ids=move_ids, user_id=user_id)
            if order_id:
                order = await self.env['order'].service.get(order_id, for_update=True)
                order.status = OrderStatus.CONFIRMED
                self.session.add(order)
                await order.notify('update')
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            await self.session.commit()
            logging.error("Произошла ошибка: %s", e)
            logging.error("Трейсбек ошибки:\n%s", traceback.format_exc())
            raise e
        return {
            "status": "OK",
            "detail": "Move is confirmed"
        }

    async def _set_src_quant(self, move: Move, quants: List[Quant], location_src):
        """
            Подбор подходящего кванта, или создание кванта
        """
        location = self.env['location']
        location_type = self.env['location_type']
        quant = self.env['quant']
        qty_to_move = 0.0
        quant_src_entity = None
        quantity = move.quantity
        quants_to_remove: List = []
        for src_quant in quants:
            if move.uom_id != src_quant.uom_id:
                continue  # TODO: единицы измерения
            if src_quant.available_quantity <= 0.0:
                continue
            if quantity <= src_quant.available_quantity:
                qty_to_move += quantity
                quantity = 0.0
                quant_src_entity = src_quant
                break
            quantity -= src_quant.available_quantity
            qty_to_move += src_quant.available_quantity
            quant_src_entity = src_quant
            quants_to_remove.append(src_quant)
            break

        if quantity:
            for src_quant in quants:
                if move.uom_id != src_quant.uom_id:
                    continue  # TODO: единицы измерения
                if not src_quant.location_rel:
                    src_quant.location_rel = await location.service.get(
                        src_quant.location_id, joined=['location_type_rel']
                    )
                location_type = await location_type.service.get(src_quant.location_rel.location_type_id)
                if location_type.is_can_negative:
                    qty_to_move += quantity
                    quantity = 0.0
                    quant_src_entity = src_quant
                    quants_to_remove.append(src_quant)
                    break
            else:
                logger.warning('The number in the move has been reduced')
                qty_to_move -= quantity
        if not quant_src_entity and location_src:
            for loc in location_src:
                if not loc.location_type_rel:
                    loc.location_type_rel = await location_type.service.get(loc.location_type_id)
                if loc.location_type_rel.is_can_negative:
                    quant_src_entity = quant.model(**{
                        "product_id": move.product_id,
                        "company_id": loc.company_id,
                        "store_id": move.store_id,
                        "location_id": loc.id,
                        "location_class": loc.location_class,
                        "lot_id": move.lot_id,
                        "partner_id": move.partner_id,
                        "quantity": 0.0,
                        "reserved_quantity": 0.0,
                        "incoming_quantity": 0.0,
                        "uom_id": move.uom_id,
                    })
                    quant_src_entity.location_rel = loc
        if not quant_src_entity:
            raise ModuleException(status_code=406, enum=MoveErrors.SOURCE_QUANT_ERROR)
        move.quantity = qty_to_move
        move.quant_src_rel = quant_src_entity
        quants = [quant for quant in quants if quant not in quants_to_remove]

    async def _set_dest_quant(self, move: Move, locations_dest: List):
        """
         Подбор подходящего кванта
        """
        quant = self.env['quant']
        quant_dest_entity = None
        available_dest_quants = await quant.service.get_available_quants(
            product_ids=[move.product_id, ],
            store_id=move.store_id,
            location_ids=[i.id for i in locations_dest],
            lot_ids=[move.lot_id] if move.lot_id else None,
            partner_id=move.partner_id if move.partner_id else None
        )
        if available_dest_quants:
            quant_dest_entity = available_dest_quants[0]
        if not available_dest_quants:
            """Поиск локаций, которые могут быть negative"""
            for loc_dest in locations_dest:
                quant_dest_entity = quant.model(**{
                    "product_id": move.product_id,
                    "company_id": move.company_id,
                    "store_id": move.store_id,
                    "location_id": loc_dest.id,
                    "location_class": loc_dest.location_class,
                    "lot_id": move.lot_id if move.lot_id else None,
                    "partner_id": move.partner_id if move.partner_id else None,
                    "quantity": 0.0,
                    "reserved_quantity": 0.0,
                    "incoming_quantity": 0.0,
                    "uom_id": move.uom_id,
                })
                quant_dest_entity.location_rel = loc_dest
                break
        if not quant_dest_entity:
            raise ModuleException(status_code=406, enum=MoveErrors.DEST_QUANT_ERROR)
        move.quant_dest_rel = quant_dest_entity

    async def _get_quants_and_allowed_locations_by_moves(self, moves: List[Move]) -> dict:
        """
            Метод разбиваем мувы на парметры, для поиска квантов и подбирает для каждой
            группы мувов подходящие кванты, и возвращает словарь словарей с ключем из move.group_key
             'products': new_products,
            'packages': new_packages,
            'location_src': locations_src,
            'available_src_quants': available_src_quants
        """
        grouped_moves = defaultdict(list)
        # Группируем мувы по параметрам
        for move in moves:
            key = move.group_key
            grouped_moves[key].append(move)

        results = {}
        for key, group in grouped_moves.items():
            params = {
                'store_id': group[0].store_id,
                'partner_id': group[0].partner_id,
                'order_type_id': key[4],
                'location_src_id': key[0],
                'location_dest_id': key[1],
                'products': [move.product_id for move in group],
                'packages': [move.package_id for move in group if move.package_id],
                'lot_ids': [key[2]],
                'move_type': key[3],
            }
            result = await self._get_quants_and_allowed_locations_by_params(**params)
            results[key] = result
        return results

    async def _fill_move_by_result(self, move: Move, prepared_result: dict):
        """
            Метод на основании параметров подобранных квантов заполняет мув
        """
        prepared_products = prepared_result['products']
        location_src = prepared_result['location_src']
        prepared_map = prepared_products[0]['order_type']
        prepared_order_type = prepared_map['order_type']
        prepared_allowed_dest_zone_ids = prepared_map['allowed_zone_ids']
        prepared_quants = prepared_products[0]['quants']
        prepared_allowed_dest_location_type_ids = prepared_map['allowed_location_type_ids']

        #  Выбор кванта источника
        await self._set_src_quant(
            move=move,
            quants=prepared_quants if prepared_products else [],
            location_src=location_src,
        )
        available_dest_locations = await self.get_avalible_locations(
            allowed_zone_ids=prepared_allowed_dest_zone_ids,
            allowed_location_type_ids=prepared_allowed_dest_location_type_ids,
        )
        if not available_dest_locations:
            raise ModuleException(status_code=406, enum=MoveErrors.DESTINATION_LOCATION_ERROR)
        # Выбор кванта назначения
        await self._set_dest_quant(move, available_dest_locations)

        if move.quant_src_id == move.quant_dest_id:
            raise ModuleException(status_code=406, enum=MoveErrors.EQUAL_QUANT_ERROR)
        # TODO: это надо убрать в отдельный вызов

    async def _moves_confirm(self, move_ids: List[UUID] | List[Move], user_id: str):
        """
        Входом для конфирма Мува может быть
         - Order - когда человек или система целенаправлено создают некий Ордер ( Ордер на примеку или Ордер на перемещение)
         - OrderType - когда Выбирается некий тип(правила) применяемые к определенному обьекту, Товарру/Упаковке
         - Move - Когда идет двуэтапное движение, тогда правила беруться из Родительского Мува
         - None - Тогда система подберет автоматически OrderType согласно подходящем

         Стратегия такова
         Если указана локация в move, то проверяется допустимость этой локации согласно правилам OrderType
         Если указан Quant, то сразу идем в Quant и фильтруем только его
         Если локация не указана, то поиск доступных квантов будет происходить в допустимых в OrderType
        """
        if not move_ids:
            raise ModuleException(status_code=406, enum=MoveErrors.MOVE_ID_ERROR)
        if move_ids and isinstance(move_ids[0], UUID) or move_ids and isinstance(move_ids[0], str):
            moves = await self.list({'id__in': move_ids})
        elif move_ids and isinstance(move_ids[0], Move):
            moves = move_ids
        else:
            raise ModuleException(status_code=406, enum=MoveErrors.MOVE_ID_ERROR)

        # Получить поисковые параметры мувов
        prepared_results = await self._get_quants_and_allowed_locations_by_moves(moves)

        for move in moves:
            if move.status == MoveStatus.CONFIRMED:
                continue
            if move.type == MoveType.PRODUCT:
                prepared_result_by_move = prepared_results[move.group_key]
                await self._fill_move_by_result(move, prepared_result_by_move)
                await self.set_reserve(move=move)

        return moves

    async def get_avalible_locations(
            self,
            allowed_zone_ids: List[UUID],
            allowed_location_type_ids: List[UUID],
            allowed_location_classes: Optional[List[str]] = None,
    ):
        """ ПОДБОР DEST ЛОКАЦИИ"""
        location = self.env['location']
        location_ids = await location.service.get_location_hierarchy(
            location_ids=allowed_zone_ids,
            location_type_ids=allowed_location_type_ids,
            location_classes=allowed_location_classes,
        )
        # TODO: здесь нужно вставить метод FEFO, FIFO, LIFO, LEFO
        return location_ids

    async def get_product_destination_quants_by_move(self, move: Move):
        """ ПОИСК КВАНТА/ЛОКАЦИИ НАЗНАЧЕНИЯ """
        """ Если у муве насильно указали location_dest_id"""
        """ Нужно проверить, что данная локация подходит под правила OrderType и правила самой выбранной локации"""
        available_dest_quants = []
        quant = self.env['quant']
        location = self.env['location']
        order_type_entity = await self.env['order_type'].service.get(move.order_type_id)

        # Достаем все локации, которые подходят под правила OrderType
        location_dest_ids = location.service.get_location_hierarchy(
            location_ids=order_type_entity.allowed_location_class_dest_ids,
            exclude_location_ids=order_type_entity.exclude_location_dest_ids,
            location_type_ids=order_type_entity.allowed_location_type_dest_ids,
            exclude_location_type_ids=order_type_entity.exclude_location_type_dest_ids,
            location_class_ids=order_type_entity.allowed_location_dest_ids,
            exclude_location_class_ids=order_type_entity.exclude_location_class_dest_ids,
        )
        available_dest_quants = await quant.service.get_available_quants(
            product_id=move.product_id,
            store_id=move.store_id,
            id=move.quant_dest_id,
            exclude_id=move.quant_src_id,  # Исключаем из возможного поиска квант источника, ибо нехер
            location_ids=[i.id for i in location_dest_ids],
            lot_ids=[move.lot_id] if move.lot_id else None,
            partner_id=move.partner_id if move.partner_id else None
        )
        # TODO: здесь нужно вставить метод Putaway
        if not available_dest_quants:
            """Поиск локаций, которые могут быть negative"""
            for loc_dest in location_dest_ids:
                quant_dest_entity = quant.model(**{
                    "product_id": move.product_id,
                    "company_id": move.company_id,
                    "store_id": move.store_id,
                    "location_id": loc_dest.id,
                    "lot_id": move.lot_id if move.lot_id else None,
                    "partner_id": move.partner_id if move.partner_id else None,
                    "quantity": 0.0,
                    "reserved_quantity": 0.0,
                    "incoming_quantity": 0.0,
                    "uom_id": move.uom_id,
                })
                available_dest_quants = [quant_dest_entity, ]
                break
        return available_dest_quants

    async def set_reserve(self, move: Move):
        """
            Здесь создается mov_log, для резервирования квантов
        """
        move_log_model = self.env['move_log'].model
        if move.type == 'product':
            """Берем обьекты на изменение"""
            # self.session.refresh(src_quant, with_for_update=True)
            # self.session.refresh(dest_quant, with_for_update=True)
            """Создаем MoveLog на резервирование товара, когда товар меняет одно из свойств таблицы, """
            """если движение на перемещение упаковки, то нет нужны """
            src_type, dest_type = TYPE_MAP.get((move.quant_src_rel.location_class, move.quant_dest_rel.location_class))
            total_quantity = move.quantity
            # Пепепроверяем, что остатка в кванте источнике достаточно для движения
            if not move.quant_src_rel.available_quantity >= total_quantity:
                locations_src = await self.env['location'].service.get(move.quant_src_rel.location_id,
                                                                       joined=['location_type_rel'])
                if not locations_src.location_type_rel:
                    location_type_rel = await self.env['location_type'].service.get(locations_src.location_type_id)
                    if not location_type_rel.is_can_negative:
                        raise ModuleException(status_code=406, enum=MoveErrors.SOURCE_QUANT_ERROR)
                else:
                    if not locations_src.location_type_rel.is_can_negative:
                        raise ModuleException(status_code=406, enum=MoveErrors.SOURCE_QUANT_ERROR)
            # Проверяем, что у мува уже не созданы саджесты
            if move.suggest_list_rel:
                raise ModuleException(status_code=406, enum=MoveErrors.SUGGESTS_ALREADY_CREATED)
            # Проверяем, что не созданы уже резервы для этого мува
            if await self.env['move_log'].service.list({'move_id': move.id}):
                raise ModuleException(status_code=406, enum=MoveErrors.RESERVATION_ALREADY_CREATED)

            # - Движение src
            src_log = move_log_model(**{
                "company_id": move.company_id,
                "type": src_type,
                "order_id": move.order_id,
                "move_id": move.id,
                "created_by": move.created_by,
                "edited_by": move.edited_by,
                "product_id": move.product_id,
                "store_id": move.store_id,
                "location_class": move.quant_src_rel.location_class,
                "location_id": move.location_src_id,
                "lot_id": move.lot_id if move.lot_id else None,
                "partner_id": move.partner_id if move.partner_id else None,
                "quantity": 0.0,
                "reserved_quantity": total_quantity,
                "incoming_quantity": 0.0,
                "uom_id": move.uom_id,
            })

            move.quant_src_rel.reserved_quantity += total_quantity

            dest_log = move_log_model(**{
                "company_id": move.company_id,
                "type": dest_type,
                "order_id": move.order_id,
                "move_id": move.id,
                "product_id": move.product_id,
                "created_by": move.created_by,
                "edited_by": move.edited_by,
                "store_id": move.store_id,
                "location_class": move.quant_dest_rel.location_class,
                "location_id": move.location_dest_id,
                "lot_id": move.lot_id if move.lot_id else None,
                "partner_id": move.partner_id if move.partner_id else None,
                "quantity": 0.0,
                "reserved_quantity": 0.0,
                "incoming_quantity": total_quantity,
                "uom_id": move.uom_id,
            })
            move.quant_dest_rel.incoming_quantity += total_quantity
            move.status = MoveStatus.CONFIRMED

            if not move.quant_src_rel.move_ids:
                move.quant_src_rel.move_ids = [move.id]
            else:
                move.quant_src_rel.move_ids.append(move.id)

            if not move.quant_dest_rel.move_ids:
                move.quant_dest_rel.move_ids = [move.id]
            else:
                move.quant_dest_rel.move_ids.append(move.id)
            self.session.add(src_log)
            self.session.add(dest_log)
            self.session.add(move)
        return move

    @estatus('processing', 'setting_done')
    @list_brocker.task(queue_name='model')
    async def set_done(self, move_id: str, user_id: str):
        self = self or list_brocker.state.data['env'].get_env()['move'].service
        move = await self.get(move_id, for_update=True)
        try:
            await self._set_done(move=move, user_id=user_id)
            move.status = MoveStatus.COMPLETE
            await self.session.commit()
            await self.session.refresh(move)
            await move.notify('update')
        except Exception as e:
            await self.session.rollback()
            self.session.refresh(move, with_for_update=True)
            move.status = MoveStatus.PROCESSING
            await self.session.commit()
            await self.session.refresh(move)
            await move.notify('update')
            logging.error("Произошла ошибка: %s", e)
            logging.error("Трейсбек ошибки:\n%s", traceback.format_exc())
            raise e

    async def _set_done(self, move: Move, user_id: str):
        """
            Здесь создается mov_log, когда все саджесты выполнены
        """
        move_log_model = self.env['move_log'].model

        src_quant = await self.env['quant'].service.get(move.quant_src_id, for_update=True)
        dest_quant = await self.env['quant'].service.get(move.quant_dest_id, for_update=True)
        location_src = await self.env['location'].service.get(move.location_src_id)
        location_dest = await self.env['location'].service.get(move.location_dest_id)
        src_type, dest_type = TYPE_MAP.get((location_src.location_class, location_dest.location_class))
        if move.status == MoveStatus.COMPLETE:
            raise ModuleException(status_code=406, enum=MoveErrors.WRONG_STATUS, args={'staus': move.status})
        if move.type == 'product':
            """Проверочки"""
            # Проверяем, что у мува все саджесты закрыты
            for suggest in move.suggest_list_rel:
                if not suggest.status == SuggestStatus.DONE:
                    raise ModuleException(status_code=406, enum=MoveErrors.SUGGESTS_NOT_DONE)

            """Создаем MoveLog только для записей, когда товар меняет одно из свойств таблицы, """
            """если движение на перемещение упаковки, то нет нужны """
            total_quantity = sum(
                float(s.result_value) for s in move.suggest_list_rel if s.type == SuggestType.IN_QUANTITY)
            move_logs = await self.env['move_log'].service.list({'move_id__in': [move.id]})
            reserve_quantity = sum(float(s.reserved_quantity) for s in move_logs)
            incoming_quantity = sum(float(s.incoming_quantity) for s in move_logs)

            # - Движение src
            src_log = move_log_model(**{
                "company_id": move.company_id,
                "type": src_type,
                "order_id": move.order_id,
                "move_id": move.id,
                "created_by": user_id,
                "edited_by": user_id,
                "product_id": move.product_id,
                "store_id": move.store_id,
                "location_class": location_src.location_class,
                "location_id": move.location_src_id,
                "lot_id": move.lot_id if move.lot_id else None,
                "partner_id": move.partner_id if move.partner_id else None,
                "quantity": -total_quantity,
                "reserved_quantity": -reserve_quantity,
                "incoming_quantity": 0.0,
                "uom_id": move.uom_id,
            })
            src_quant.reserved_quantity -= reserve_quantity
            src_quant.quantity -= total_quantity
            origin_quant_dest_id = move.vars.get('origin_quant_dest_id')
            if origin_quant_dest_id:
                origin_quant_dest = await self.env['quant'].service.get(origin_quant_dest_id, for_update=True)
                # Если у мува есть исходный квант назначения, то освобождаем его
                origin_quant_log = move_log_model(**{
                    "company_id": origin_quant_dest.company_id,
                    "type": dest_type,
                    "order_id": move.order_id,
                    "move_id": move.id,
                    "product_id": origin_quant_dest.product_id,
                    "created_by": user_id,
                    "edited_by": user_id,
                    "store_id": move.store_id,
                    "location_class": origin_quant_dest.location_class,
                    "location_id": origin_quant_dest.location_in,
                    "lot_id": origin_quant_dest.lot_id if origin_quant_dest.lot_id else None,
                    "partner_id": origin_quant_dest.partner_id if origin_quant_dest.partner_id else None,
                    "quantity": 0.0,
                    "reserved_quantity": 0.0,
                    "incoming_quantity": -incoming_quantity,
                    "uom_id": origin_quant_dest.uom_id,
                })
                origin_quant_dest.incoming_quantity -= incoming_quantity
                self.session.add(origin_quant_log)

            dest_log = move_log_model(**{
                "company_id": move.company_id,
                "type": dest_type,
                "order_id": move.order_id,
                "move_id": move.id,
                "product_id": move.product_id,
                "created_by": user_id,
                "edited_by": user_id,
                "store_id": move.store_id,
                "location_class": location_dest.location_class,
                "location_id": move.location_dest_id,
                "lot_id": move.lot_id if move.lot_id else None,
                "partner_id": move.partner_id if move.partner_id else None,
                "quantity": total_quantity,
                "reserved_quantity": 0.0,
                "incoming_quantity": -incoming_quantity if not origin_quant_dest_id else 0.0,
                "uom_id": move.uom_id,
            })

            dest_quant.incoming_quantity -= incoming_quantity
            dest_quant.quantity += total_quantity
            if move.id in src_quant.move_ids:
                src_quant.move_ids.remove(move.id)
            if move.id in dest_quant.move_ids:
                dest_quant.move_ids.remove(move.id)

            self.session.add(src_quant)
            self.session.add(src_log)
            self.session.add(dest_quant)
            self.session.add(dest_log)

    @permit('move_create')
    async def create(self, obj: CreateSchemaType, parent: Order | Move | None = None, commit=True) -> ModelType:
        obj.created_by = self.user.user_id
        obj.edited_by = self.user.user_id
        return await super(MoveService, self).create(obj)

    @permit('move_delete')
    async def delete(self, id: UUID) -> None:
        if isinstance(id, UUID):
            move = await self.get(id)
            if move.status != MoveStatus.CREATED:
                raise ModuleException(status_code=406, enum=MoveErrors.WRONG_STATUS)
        return await super(MoveService, self).delete(id)

    @permit('get_moves_by_barcode')
    async def get_moves_by_barcode(self, barcode: str, order_id: UUID) -> List[ModelType]:
        """
            Если прикрепился пользователь, то значит, что необходимо создать саджесты для выполнения
        """
        query = select(self.model)
        product_obj = await self.env['product'].adapter.product_by_barcode(barcode)
        if order_id:
            query = query.where(self.model.order_id == order_id)
        query = query.where(self.model.product_id == product_obj.id)
        executed_data = await self.session.execute(query)
        move_entities = executed_data.scalars().all()
        return move_entities

    @permit('change_dest_location')
    async def change_dest_location(self, move: Move, location: 'Location'):
        # Меняем ячейку и ищем квант назначения
        move.vars.update({
            'origin_location_dest_id': move.location_dest_id,
            'origin_quant_dest_id': move.quant_dest_id
        })
        dest_quant = self.env['quant'].service.get(move.quant_dest_id)
        dest_quant.move_ids.remove(move.id)
        self.session.add(dest_quant)
        move.location_dest_id = location.id
        move.quant_dest_id = None
        available_quants = await self.get_product_destination_quants_by_move(move=move)
        if not available_quants:
            raise ModuleException(
                status_code=406,
                enum=MoveErrors.CHANGE_LOCATION_ERROR
            )
        new_quant = available_quants[0]
        self.session.add(new_quant)
        if not new_quant.id:
            await self.session.flush([new_quant])
        new_quant.move_ids.append(move.id)
        move.quant_dest_id = new_quant.id

    async def _get_quants_and_allowed_locations_by_params(
            self,
            store_id: UUID,
            partner_id: Optional[UUID] = None,
            order_type_id: Optional[UUID] = None,
            location_src_id: Optional[UUID] = None,
            location_src_zone_id: Optional[UUID] = None,
            location_dest_id: Optional[UUID] = None,
            location_dest_zone_id: Optional[UUID] = None,
            location_type_src_id: Optional[UUID] = None,
            products: Optional[List[UUID]] | List[dict] = None,  # type: ignore
            packages: Optional[List[UUID] | List[dict]] = None,
            lot_ids: Optional[List[UUID]] = None,
            move_type: Optional[MoveType] = None,
            **kwargs: Any
    ):  # type: ignore
        """
        Метод принимает на вход параметры, которые позволяют подготовить перемещения
        Метод отдает словарь products, packages, location_src, location_dest
        products - список продуктов, возможные для выбора order_types и кванты подходящие под параметры
        packages - список упаковок подходящие под параметры с содеожимым квантов
        location_src - список локаций источников поиска квантов
        available_src_quants - список всех найденных подобранных квантов вообще

        """
        if lot_ids is None:
            lot_ids = []
        if products:
            if isinstance(products[0], dict):
                # Преобразовываем, если на вход прилетело так
                lot_ids += [product['lot_id'] for product in products if product['lot_id'] is not None]  # type: ignore
                products = [product['product_id'] for product in products]  # type: ignore

        if packages:
            if isinstance(packages[0], dict):
                # Преобразовываем, если на вход прилетело так
                packages = [package['package_id'] for package in packages]  # type: ignore

        """
         Метод позволяет по разным параметрам создать перемещение товаров
        """
        quant_model: Model = self.env['quant']
        order_type_model: Model = self.env['order_type']
        location_model: Model = self.env['location']
        locations_src: list[Location] = []
        # 1 - Сначала надо подобрать order_type_id, если его нет
        # 2 - Берем все типы ордеров, у которых класс internal
        location_class_src = list(PhysicalLocationClass)
        if not order_type_id:
            order_types: List[OrderType] = await order_type_model.service.list({
                'order_class__in': [OrderClass.INTERNAL],
            })
        else:
            order_types: List[OrderType] = await order_type_model.service.list(
                {'id__in': [order_type_id]})  # type: ignore
            # type: ignore
        for ot in order_types:
            if ot.order_class == OrderClass.INCOMING:
                location_class_src = [LocationClass.PARTNER, ]
            elif ot.order_class == OrderClass.OUTGOING:
                location_class_src = [LocationClass.PARTNER, ]
        assert any([location_src_zone_id, location_src_id, location_type_src_id, products, packages]), \
            'Должно быть заполнено чет одно'
        assert order_types, 'Не найдено ни одного типа ордера'
        if location_src_id:
            # Если указана локация, то достаем ее, а на зону уже не обращаем внимание
            locations_src = [await location_model.service.get(location_src_id), ]
        elif location_src_zone_id:
            # Если указана зона, достаем ее дочерние подзоны так же, что бы найти все физические зоны
            locations_src = await location_model.service.get_location_hierarchy(
                location_ids=[location_src_zone_id],
                location_type_ids=[location_type_src_id],
            )
        else:
            # Если не указана локация, то ищем все локации, которые подходят под правила OrderType
            locations_src = await location_model.service.list({
                'location_class__in': location_class_src,
                'store_id__in': [store_id],
            })
        # for loc in locations_src:
        #     # Если указана локация НЕ физическая зона, то выдаем ошибку
        #     if loc.location_class not in list(PhysicalLocationClass):
        #         raise ModuleException(
        #             status_code=406, enum=MoveErrors.SOURCE_LOCATION_ERROR,
        #             message='The source location must be Physical a zone',
        #             args={'location_id': loc.id}
        #         )

        available_src_quants = await quant_model.service.get_available_quants(
            store_id=store_id,
            location_ids={i.id for i in locations_src},
            product_ids={i for i in products} if products else None,
            package_ids={i for i in packages} if packages else None,
            partner_id=partner_id if partner_id else None,
            location_classes=location_class_src,
            lot_ids=lot_ids if lot_ids else None,
        )

        packages_map = defaultdict(list)  # type: ignore
        for q in available_src_quants:
            if q.package_id:
                packages_map[q.package_id].append(q)
        new_packages: List = []
        if move_type is None or move_type == MoveType.PACKAGE:
            for pack in packages_map:
                # Сравниваем найденные кванты и берем упаковки из бд, если они идентичны, считаем, что все в этих package_id
                # Перемещаем как Упаковки
                pack_quants = await quant_model.service.list({'package_id__in': [pack]})
                identical = compare_lists(pack_quants, packages_map[pack])
                if identical:
                    # Удаляем из доступных для отбора квантов
                    available_src_quants = [item for item in available_src_quants if item not in pack_quants]
                    # Добавляем в новый список
                    new_packages.append({
                        'package_id': pack,
                        'quants': pack_quants
                    })
            # TODO: надо ли package_order_type_map сортировать?
            package_order_type_map = await order_type_model.service.get_appropriate_order_types_for_packages(
                packages=[(i['package_id'], q.location_id) for i in new_packages for q in i['quants'] if i['quants']],
                zone_dest_id=location_dest_zone_id,
                location_dest_id=location_dest_id,
                order_types=order_types,
                partner_id=partner_id,
                store_id=store_id
            )
            for pack in new_packages:
                pack_order_types = package_order_type_map.get(pack['package_id'])
                pack['order_type'] = pack_order_types[0]
                pack['location_dest_id'] = location_dest_id

        new_products: List = []
        if move_type is None or move_type == MoveType.PRODUCT:
            grouped_quants: defaultdict[Any, dict[str, float | list]] = defaultdict(
                lambda: {'quantity': 0.0, 'available_quantity': 0.0, 'quants': []}
            )
            for quant in available_src_quants:
                key = (quant.product_id, quant.lot_id, quant.uom_id, quant.partner_id)
                grouped_quants[key]['quantity'] += quant.quantity
                grouped_quants[key]['available_quantity'] += quant.available_quantity
                grouped_quants[key]['quants'].append(quant)  # type: ignore

            # Добавляем товары из products, для которых не нашлось квантов
            for product_id in products:  # type: ignore
                if not any(key[0] == product_id for key in grouped_quants):
                    key = (product_id, None, None, None)
                    grouped_quants[key] = {'quantity': 0.0, 'available_quantity': 0.0, 'quants': []}

            # TODO: надо ли product_order_types_map сортировать?
            product_order_types_map = await order_type_model.service.get_appropriate_order_types(
                products=[
                             (q.product_id, q.location_id) for key, data in grouped_quants.items() for q in
                             data['quants']  # type: ignore
                         ] + [
                             (key[0], loc.id) for key, data in grouped_quants.items() if not data['quants'] for loc in
                             locations_src
                         ],
                zone_dest_id=location_dest_zone_id,
                location_dest_id=location_dest_id,
                order_types=order_types,
                store_id=store_id,
                partner_id=partner_id
            )
            # Создаем модели Product на основе сгруппированных данных

            for key, data in grouped_quants.items():
                order_types = product_order_types_map.get(key[0])
                if order_types is None:
                    raise ValueError(f"Order types not found for product_id: {key[0]}")
                new_products.append({
                    'product_id': key[0],
                    'lot_id': key[1],
                    'uom_id': key[2],
                    'order_type': order_types[0],
                    'partner_id': key[3],
                    'quantity': data['quantity'],
                    'avaliable_quantity': data['available_quantity'],
                    'quants': data['quants'],
                    'location_dest_id': location_dest_id  # type: ignore
                })
        return {
            'products': new_products,
            'packages': new_packages,
            'location_src': locations_src,
            'available_src_quants': available_src_quants
        }
    async def _create_moves_by_params(self, prepared_products: dict):
        """
            Создание мувов по параметрам
        """
        for product in prepared_products:
            for quant in product['quants']:
                move = self.model(
                    product_id=quant.product_id,
                    lot_id=quant.lot_id,
                    uom_id=quant.uom_id,
                    order_type_id=product['order_type'].id,
                    partner_id=quant.partner_id,
                    quantity=product.quantity,
                )
                await self.create(move)
            move = self.model(
                product_id=i['product_id'],
                lot_id=i['lot_id'],
                uom_id=i['uom_id'],
                order_type_id=i['order_type'].id,
                partner_id=i['partner_id'],
                quantity=i['quantity'],
                avaliable_quantity=i['avaliable_quantity'],
                location_src_id=i['location_src_id'],
                location_dest_id=i['location_dest_id'],
            )

        move = self.model(**params)
        return move
    async def create_movements(self, schema: CreateMovements):
        prepared_data = await self._get_quants_and_allowed_locations_by_params(**schema.model_dump())
        products: List[Product] = []
        for i in prepared_data['products']:
            moves: List[Move] = []
            qty_to_move = i['quantity']
            for q in i['quants']:
                qty_move = 0.0
                if qty_to_move <= 0.0:
                    continue
                if q.available_quantity >= qty_to_move:
                    qty_move = qty_to_move
                    qty_to_move = 0.0
                elif q.available_quantity < qty_to_move:
                    qty_move = q.available_quantity
                    qty_to_move -= qty_move
                moves.append(Move(
                    type=MoveType.PRODUCT,
                    product_id=q.product_id,
                    store_id=q.store_id,
                    lot_id=q.lot_id,
                    uom_id=q.uom_id,
                    quantity=qty_move,
                    order_type_id=i['order_type']['order_type'].id,
                    partner_id=q.partner_id,
                    location_src_id=q.location_id,
                    quant_src_id=q.id,
                ))
            products.append(
                Product(
                    product_id=i['product_id'],
                    lot_id=i['lot_id'],
                    uom_id=i['uom_id'],
                    quantity=i['quantity'],
                    avaliable_quantity=i['avaliable_quantity'],
                    quants=i['quants'],
                    moves=moves
                )
            )
            schema.products = products
        return schema
