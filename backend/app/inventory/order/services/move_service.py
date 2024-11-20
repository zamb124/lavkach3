import logging
import logging
import traceback
import typing

from typing import Any, Optional, List

from sqlalchemy import select, Row
from starlette.requests import Request
from uuid import UUID

from app.inventory.estatus import estatus
from app.inventory.location.enums import VirtualLocationZones
from app.inventory.order.enums.exceptions_move_enums import MoveErrors
from app.inventory.order.enums.order_enum import OrderStatus, SuggestStatus, TYPE_MAP
from app.inventory.order.models.order_models import Move, MoveType, Order, MoveStatus, \
    SuggestType
from app.inventory.order.schemas.move_schemas import MoveCreateScheme, MoveUpdateScheme, MoveFilter
from app.inventory.quant import Quant
from core.exceptions.module import ModuleException
# from app.inventory.order.services.move_tkq import move_set_done
from core.helpers.broker import list_brocker
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType

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
    async def create_suggests(self, move_ids: list, user_id: str):
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
    async def confirm(self, move_ids: str, user_id: str, order_id: UUID = None):
        self = self or list_brocker.state.data['env'].get_env()['move'].service
        orders = []
        try:
            for move_id in move_ids:
                move = await self.check_func_status_get_entity(self.confirm, move_id, for_update=True)
                await self._confirm(move=move, user_id=user_id)
                #orders.append(move.order_rel)
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

    async def _confirm(self, move: Row, user_id: str):
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
        if move.status == MoveStatus.CONFIRMED:
            return move
        order_type = self.env['order_type']
        quant = self.env['quant']
        location = self.env['location']
        if move.type == MoveType.PRODUCT:
            quant_src_entity: Quant | None = None
            quant_dest_entity: Quant | None = None
            qty_to_move = 0.0
            order_type = await order_type.service.get(move.order_type_id)
            available_src_locations = await self.get_avalible_locations(
                allowed_zone_ids=order_type.allowed_zone_src_ids,
                exclude_zone_ids=order_type.exclude_zone_src_ids,
                allowed_location_type_ids=order_type.allowed_location_type_src_ids,
                exclude_location_type_ids=order_type.exclude_location_type_src_ids,
                allowed_location_class=order_type.allowed_location_class_src_ids,
                exclude_location_class=order_type.exclude_location_class_src_ids,
            )
            if not available_src_locations:
                raise ModuleException(status_code=406, enum=MoveErrors.SOURCE_LOCATION_ERROR)
            available_src_quants = await quant.service.get_available_quants(
                product_ids=[move.product_id,],
                store_id=move.store_id,
                location_ids=[i.id for i in available_src_locations],
                lot_ids=[move.lot_id] if move.lot_id else None,
                partner_id=move.partner_id if move.partner_id else None
            )
            remainder = move.quantity
            if available_src_quants:
                for src_quant in available_src_quants:
                    if move.uom_id != src_quant.uom_id:
                        continue  # TODO: единицы измерения

                    if src_quant.available_quantity <= 0.0:
                        continue

                    if remainder <= src_quant.available_quantity:
                        qty_to_move += remainder
                        remainder = 0.0
                        quant_src_entity = src_quant
                        break

                    remainder -= src_quant.available_quantity
                    qty_to_move += src_quant.available_quantity
                    quant_src_entity = src_quant
                    break

                if remainder:
                    if remainder == move.quantity:
                        for src_quant in available_src_quants:
                            if move.uom_id != src_quant.uom_id:
                                continue  # TODO: единицы измерения

                            q_location = await location.service.get(src_quant.location_id)
                            if q_location.location_type_rel.is_can_negative:
                                qty_to_move += remainder
                                remainder = 0.0
                                quant_src_entity = src_quant
                                break
                    else:
                        logger.warning('The number in the move has been reduced')
                        move.quantity -= remainder
            else:
                for loc_src in available_src_locations:
                    if loc_src.location_type_rel.is_can_negative:
                        quant_src_entity = quant.model(**{
                            "product_id": move.product_id,
                            "company_id": move.company_id,
                            "store_id": move.store_id,
                            "location_id": loc_src.id,
                            "location_class": loc_src.location_class,
                            "lot_id": move.lot_id if move.lot_id else None,
                            "partner_id": move.partner_id if move.partner_id else None,
                            "quantity": 0.0,
                            "reserved_quantity": 0.0,
                            "incoming_quantity": 0.0,
                            "uom_id": move.uom_id,
                        })
                        break
            if not quant_src_entity:
                raise ModuleException(status_code=406, enum=MoveErrors.SOURCE_QUANT_ERROR)

            available_dest_locations = await self.get_avalible_locations(
                allowed_zone_ids=order_type.allowed_zone_dest_ids,
                exclude_zone_ids=order_type.exclude_zone_dest_ids,
                allowed_location_type_ids=order_type.allowed_location_type_dest_ids,
                exclude_location_type_ids=order_type.exclude_location_type_dest_ids,
                allowed_location_class=order_type.allowed_location_class_dest_ids,
                exclude_location_class=order_type.exclude_location_class_dest_ids,
            )
            if not available_dest_locations:
                raise ModuleException(status_code=406, enum=MoveErrors.DESTINATION_LOCATION_ERROR)
            available_dest_quants = await quant.service.get_available_quants(
                product_ids=[move.product_id,],
                store_id=move.store_id,
                location_ids=[i.id for i in available_dest_locations],
                lot_ids=[move.lot_id] if move.lot_id else None,
                partner_id=move.partner_id if move.partner_id else None
            )
            if not available_dest_quants:
                """Поиск локаций, которые могут быть negative"""
                for loc_dest in available_dest_locations:
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
                    available_dest_quants = [quant_dest_entity, ]
                    break
            for dest_quant in available_dest_quants:
                quant_dest_entity = dest_quant
                # quant_dest_entity.incoming_quantity += move.quantity
                # self.session.add(quant_dest_entity)
                break

            if not quant_dest_entity:
                raise ModuleException(status_code=406, enum=MoveErrors.DEST_QUANT_ERROR)

            if quant_src_entity == quant_dest_entity:
                raise ModuleException(status_code=406, enum=MoveErrors.EQUAL_QUANT_ERROR)
            # TODO: это надо убрать в отдельный вызов
            move_logs = await self.set_reserve(
                move=move, src_quant=quant_src_entity,
                dest_quant=quant_dest_entity,
                qty_to_move=qty_to_move
            )

        return move

    async def get_avalible_locations(
            self,
            allowed_zone_ids: List[UUID],
            exclude_zone_ids: List[UUID],
            allowed_location_type_ids: List[UUID],
            exclude_location_type_ids: List[UUID],
            allowed_location_class: List[str],
            exclude_location_class: List[str],
    ):
        """ ПОДБОР ИСХОДЯЩЕГО КВАНТА/ЛОКАЦИИ"""
        location = self.env['location']
        """Проверяем, что мув может быть создан согласно праавилам в Order type """
        location_ids = await location.service.get_location_hierarchy(
            location_ids=allowed_zone_ids,
            exclude_location_ids=exclude_zone_ids,
            location_type_ids=allowed_location_type_ids,
            exclude_location_type_ids=exclude_location_type_ids,
            location_classes=allowed_location_class,
            exclude_location_classes=exclude_location_class,
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

    async def set_reserve(self, move: Row, src_quant: Quant, dest_quant: Quant, qty_to_move: float):
        """
            Здесь создается mov_log, для резервирования квантов
        """
        move_log_model = self.env['move_log'].model
        if move.type == 'product':
            """Берем обьекты на изменение"""
            #self.session.refresh(src_quant, with_for_update=True)
            #self.session.refresh(dest_quant, with_for_update=True)
            """Создаем MoveLog на резервирование товара, когда товар меняет одно из свойств таблицы, """
            """если движение на перемещение упаковки, то нет нужны """
            src_type, dest_type = TYPE_MAP.get((src_quant.location_class, dest_quant.location_class))
            total_quantity = qty_to_move
            # Пепепроверяем, что остатка в кванте источнике достаточно для движения
            if not src_quant.available_quantity >= total_quantity:
                locations_src = await self.env['location'].service.get(src_quant.location_id)
                if not locations_src.location_type_rel.is_can_negative:
                    raise ModuleException(status_code=406, enum=MoveErrors.SOURCE_QUANT_ERROR)
            # Проверяем, что у мува уже не созданы саджесты
            if move.suggest_list_rel:
                raise ModuleException(status_code=406, enum=MoveErrors.SUGGESTS_ALREADY_CREATED)
            # Проверяем, что не созданы уже резервы для этого мува
            if await self.env['move_log'].service.list({'move_id': move.id}):
                raise ModuleException(status_code=406, enum=MoveErrors.RESERVATION_ALREADY_CREATED)
            self.session.add(src_quant)
            self.session.add(dest_quant)
            await self.session.flush([src_quant, dest_quant])

            move.quant_src_id = src_quant.id
            move.location_src_id = src_quant.location_id
            move.lot_id = src_quant.lot_id
            move.partner_id = src_quant.partner_id
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
                "location_class": src_quant.location_class,
                "location_id": move.location_src_id,
                "lot_id": move.lot_id if move.lot_id else None,
                "partner_id": move.partner_id if move.partner_id else None,
                "quantity": 0.0,
                "reserved_quantity": total_quantity,
                "incoming_quantity": 0.0,
                "uom_id": move.uom_id,
            })

            src_quant.reserved_quantity += total_quantity
            move.quant_dest_id = dest_quant.id
            move.location_dest_id = dest_quant.location_id

            dest_log = move_log_model(**{
                "company_id": move.company_id,
                "type": dest_type,
                "order_id": move.order_id,
                "move_id": move.id,
                "product_id": move.product_id,
                "created_by": move.created_by,
                "edited_by": move.edited_by,
                "store_id": move.store_id,
                "location_class": dest_quant.location_class,
                "location_id": move.location_dest_id,
                "lot_id": move.lot_id if move.lot_id else None,
                "partner_id": move.partner_id if move.partner_id else None,
                "quantity": 0.0,
                "reserved_quantity": 0.0,
                "incoming_quantity": total_quantity,
                "uom_id": move.uom_id,
            })
            dest_quant.incoming_quantity += total_quantity
            move.status = MoveStatus.CONFIRMED

            if not src_quant.move_ids:
                src_quant.move_ids = [move.id]
            else:
                src_quant.move_ids.append(move.id)
            self.session.add(src_quant)

            if not dest_quant.move_ids:
                dest_quant.move_ids = [move.id]
            else:
                dest_quant.move_ids.append(move.id)
            self.session.add(src_quant)
            self.session.add(dest_quant)
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
            total_quantity = sum(float(s.value) for s in move.suggest_list_rel if s.type == SuggestType.IN_QUANTITY)
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

    @permit('move_move_counstructor')
    async def move_counstructor(self, move_id: UUID, moves: list) -> None:
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
