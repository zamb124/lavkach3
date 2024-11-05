import logging
import logging
import uuid
from typing import Any, Optional, List

from sqlalchemy import select
from starlette.exceptions import HTTPException
from starlette.requests import Request
from app.inventory.location.enums import VirtualLocationClass, PhysicalLocationClass
from app.inventory.order import MoveLog
from app.inventory.order.enums.exceptions_move_enums import MoveErrors
from app.inventory.order.enums.order_enum import MoveLogType, OrderStatus
from app.inventory.order.models.order_models import Move, MoveType, Order, OrderType, MoveStatus, \
    SuggestType
from app.inventory.order.schemas.move_schemas import MoveCreateScheme, MoveUpdateScheme, MoveFilter
from app.inventory.quant import Quant
# from app.inventory.order.services.move_tkq import move_set_done
from core.helpers.broker import list_brocker
from core.exceptions.module import ModuleException
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType
from core.utils.timeit import timed

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
    async def list(self, _filter: FilterSchemaType, size: int=100):
        return await super(MoveService, self).list(_filter, size)

    @list_brocker.task(queue_name='model')
    async def create_suggests(self=None, move: str = None):
        """
            Создаются саджесты в зависимости от OrderType и Product
        """
        self = self or list_brocker.state.data['env'].get_env()['move'].service
        if isinstance(move, str):
            move = await self.get(move)
        suggest_service = self.env['suggest'].service
        location_service = self.env['location'].service
        if move.type == MoveType.PRODUCT:
            """Если это перемещение товара из виртуальцой локации, то идентификация локации не нужна"""
            location_src = await location_service.get(move.location_src_id)
            location_dest = await location_service.get(move.location_dest_id)
            if not location_src.location_class in VirtualLocationClass:
                await suggest_service.create(obj={
                    "move_id": move.id,
                    "priority": 1,
                    "type": SuggestType.IN_LOCATION,
                    "value": f'{location_src.id}',
                    "company_id": move.company_id,
                    # "user_id": self.user.user_id
                }, commit=False)
            """Ввод Партии"""  # TODO:  пока хз как праильное
            """Далее саджест на идентификацию товара"""
            await suggest_service.create(obj={
                "move_id": move.id,
                "priority": 2,
                "type": SuggestType.IN_PRODUCT,
                "value": f'{move.product_id}',
                "company_id": move.company_id,
                # "user_id": self.user.user_id
            }, commit=False)
            """Далее саджест ввода количества"""
            await suggest_service.create(obj={
                "move_id": move.id,
                "priority": 3,
                "type": SuggestType.IN_QUANTITY,
                "value": f'{move.quantity}',
                "company_id": move.company_id,
                # "user_id": self.user.user_id
            }, commit=False)
            """Далее саджест на ввод срока годности"""  # TODO:  пока хз как праильное
            """Далее саджест идентификации локации назначения"""
            await suggest_service.create(obj={
                "move_id": move.id,
                "priority": 4,
                "type": SuggestType.IN_LOCATION,
                "value": f'{location_dest.id}',
                "company_id": move.company_id,
                # "user_id": self.user.user_id
            }, commit=False)
            await suggest_service.session.commit()
            # Итого простой кейс, отсканировал локацию-источник, отсканировал товар, отсканировал локацию-назначения

    @permit('move_user_assign')
    async def user_assign(self, move_id: uuid.UUID, user_id: uuid.UUID):
        """
            Если прикрепился пользователь, то значит, что необходимо создать саджесты для выполнения
        """
        move = await self.get(move_id)
        # await move.create_suggests()
        move.user_id = user_id
        await self.session.commit()
        return move

    @list_brocker.task(queue_name='model')
    async def confirm(self, move_ids: str, user_id: str):
        self = self or list_brocker.state.data['env'].get_env()['move'].service
        moves = await self.list({'id__in': move_ids}, size=9999)
        try:
            for move in moves:
                await self._confirm(move=move, user_id=user_id)
                a=1
            await self.session.commit()
        except Exception as ex:
            await self.session.rollback()
            try:
                order = await self.env['order'].service.get(moves[0].order_id, for_update=True)
                order.status = OrderStatus.RESERVATION_FAILED
                await self.session.commit()
            except Exception as ex:
                self.session.rollback()
                raise HTTPException(status_code=500, detail=f"ERROR:  {str(ex)}")
            raise HTTPException(status_code=500, detail=f"ERROR:  {str(ex)}")
        return {
            "status": "OK",
            "detail": "Move is confirmed"
        }


    async def _confirm(self, move: Move, user_id: str):
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
        if move.status != MoveStatus.CREATED:
            raise ModuleException(status_code=406, enum=MoveErrors.WRONG_STATUS)
        location_service = self.env['location'].service
        order_type_service = self.env['order_type'].service
        quant = self.env['quant']
        if move.type == MoveType.PRODUCT:
            """ ПОДБОР ИСХОДЯЩЕГО КВАНТА/ЛОКАЦИИ"""
            quant_src_entity: Quant | None = None
            quant_dest_entity: Quant | None = None
            qty_to_move = 0
            assert move.product_id, 'Product is required if Move Type is  Product'
            order_type_entity = await order_type_service.get(move.order_type_id)
            """Проверяем, что мув может быть создан согласно праавилам в Order type """

            location_class_src_ids = list(
                set(order_type_entity.allowed_location_class_src_ids) -
                set(order_type_entity.exclude_location_class_src_ids)
            )
            location_type_src_ids = list(
                set(order_type_entity.allowed_location_type_src_ids) -
                set(order_type_entity.exclude_location_type_src_ids)
            )
            location_src_ids = list(
                set(order_type_entity.allowed_location_src_ids) -
                set(order_type_entity.exclude_location_src_ids)
            )
            if move.location_src_id:
                """Если мы указали локацию, то нас уже не интересуют правила из OrderType"""
                location_class_src_ids, location_type_src_ids, location_src_ids = [], [], [move.location_src_id, ]

            available_src_quants = await quant.service.get_available_quants(
                product_id=move.product_id,
                store_id=move.store_id,
                id=move.quant_src_id,
                location_class_ids=location_class_src_ids,
                location_ids=location_src_ids,
                location_type_ids=location_type_src_ids,
                lot_ids=[move.lot_id] if move.lot_id else None,
                partner_id=move.partner_id if move.partner_id else None
            )
            # TODO: здесь нужно вставить метод FEFO, FIFO, LIFO, LEFO
            if not available_src_quants:
                """Поиск локаций, которые могут быть negative"""
                location_src_search_params = {
                    "location_class__in": location_class_src_ids,
                    "location_type_id__in": location_type_src_ids,
                    "id__in": location_src_ids,
                    "is_active": True,
                    "is_can_negative": True
                }
                locations_src = await location_service.list(_filter=location_src_search_params)
                for loc_src in locations_src:
                    quant_src_entity = quant.model(**{
                        "product_id": move.product_id,
                        "company_id": move.company_id,
                        "store_id": move.store_id,
                        "location_id": loc_src.id,
                        "location_class": loc_src.location_class,
                        "location_type_id": loc_src.location_type_id,
                        "lot_id": move.lot_id if move.lot_id else None,
                        "partner_id": move.partner_id if move.partner_id else None,
                        "quantity": 0.0,
                        "reserved_quantity": 0.0,
                        "incoming_quantity": 0.0,
                        "uom_id": move.uom_id,
                    })
                    available_src_quants = [quant_src_entity, ]
                    break

            if available_src_quants:
                """Если кванты нашлись"""
                remainder = move.quantity
                for src_quant in available_src_quants:
                    if move.uom_id == src_quant.uom_id:
                        if src_quant.available_quantity <= 0.0:
                            pass
                        elif remainder <= src_quant.available_quantity:
                            # src_quant.reserved_quantity += remainder
                            remainder = 0.0
                            qty_to_move += remainder
                            quant_src_entity = src_quant
                            # self.session.add(quant_src_entity)
                            break
                        elif remainder >= src_quant.available_quantity:
                            remainder -= src_quant.available_quantity
                            qty_to_move = remainder
                            # src_quant.quantity = 0.0
                            quant_src_entity = src_quant
                            # self.session.add(quant_src_entity)
                            break
                    else:
                        pass  # TODO: единицы измерения
                if remainder:
                    if remainder == move.quantity:
                        "Если не нашли свободного количества вообще"
                        "снова идем по квантам и берем то, у которого локация позволяет сделать отрицательный остсток"
                        for src_quant in available_src_quants:
                            if move.uom_id == src_quant.uom_id:
                                q_location = await location_service.get(src_quant.location_id)
                                if q_location.is_can_negative:
                                    # src_quant.reserved_quantity += remainder
                                    qty_to_move += remainder
                                    remainder = 0.0
                                    quant_src_entity = src_quant
                                    # self.session.add(quant_src_entity)
                                    break
                            else:
                                ...  # TODO: единицы измерения
                    else:
                        "Если квант нашелся, но на частичное количество уменьшаем количество в муве тк 1 мув = 1квант"
                        logger.warning(f'The number in the move has been reduced')
                        move.quantity -= remainder
            if not quant_src_entity:
                raise ModuleException(status_code=406, enum=MoveErrors.SOURCE_QUANT_ERROR)

            """ ПОИСК КВАНТА/ЛОКАЦИИ НАЗНАЧЕНИЯ """

            """ Если у муве насильно указали location_dest_id"""
            """ Нужно проверить, что данная локация подходит под правила OrderType и правила самой выбранной локации"""

            location_class_dest_ids = list(
                set(order_type_entity.allowed_location_class_dest_ids) -
                set(order_type_entity.exclude_location_class_dest_ids)
            )
            location_type_dest_ids = list(
                set(order_type_entity.allowed_location_type_dest_ids) -
                set(order_type_entity.exclude_location_type_dest_ids)
            )
            location_dest_ids = list(
                set(order_type_entity.allowed_location_dest_ids) -
                set(order_type_entity.exclude_location_dest_ids)
            )

            if move.location_dest_id:
                """Если мы указали локацию, то нас уже не интересуют правила из OrderType"""
                location_class_dest_ids, location_type_dest_ids, location_dest_ids = [], [], [move.location_dest_id, ]

            available_dest_quants = await quant.service.get_available_quants(
                product_id=move.product_id,
                store_id=move.store_id,
                id=move.quant_dest_id,
                exclude_id=quant_src_entity.id,  # Исключаем из возможного поиска квант источника, ибо нехер
                location_class_ids=location_class_dest_ids,
                location_ids=location_dest_ids,
                location_type_ids=location_type_dest_ids,
                lot_ids=[move.lot_id] if move.lot_id else None,
                partner_id=move.partner_id if move.partner_id else None
            )
            # TODO: здесь нужно вставить метод Putaway
            if not available_dest_quants:
                """Поиск локаций, которые могут быть negative"""
                location_dest_search_params = {
                    "location_class__in": location_class_dest_ids,
                    "location_type_id__in": location_type_dest_ids,
                    "id__in": location_dest_ids,
                    "is_active": True,
                }
                locations_dest = await location_service.list(_filter=location_dest_search_params)
                for loc_dest in locations_dest:
                    quant_dest_entity = quant.model(**{
                        "product_id": move.product_id,
                        "company_id": move.company_id,
                        "store_id": move.store_id,
                        "location_id": loc_dest.id,
                        "location_class": loc_dest.location_class,
                        "location_type_id": loc_dest.location_type_id,
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
            move_logs = await self.set_reserve(move=move, src_quant=quant_src_entity, dest_quant=quant_dest_entity,
                                               qty_to_move=qty_to_move)
        return move

    async def set_reserve(self, move: Move, src_quant: Quant, dest_quant: Quant, qty_to_move: float):
        """
            Здесь создается mov_log, для резервирования квантов
        """
        move_log_model = self.env['move_log'].model
        if move.type == 'product':
            type_map = {
                (VirtualLocationClass.PARTNER, PhysicalLocationClass.PLACE): (
                MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
                (VirtualLocationClass.PARTNER, PhysicalLocationClass.BUFFER): (
                MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
                (PhysicalLocationClass.PLACE, PhysicalLocationClass.PLACE): (MoveLogType.PUT_OUT, MoveLogType.PUT_IN),
                (PhysicalLocationClass.PLACE, VirtualLocationClass.PARTNER): (
                MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
                (PhysicalLocationClass.PLACE, VirtualLocationClass.INVENTORY): (
                MoveLogType.INVENROTY_OUT, MoveLogType.INVENROTY_IN),
                (VirtualLocationClass.INVENTORY, PhysicalLocationClass.PLACE): (
                MoveLogType.INVENROTY_OUT, MoveLogType.INVENROTY_IN),
                (VirtualLocationClass.LOST, PhysicalLocationClass.PLACE): (MoveLogType.LOST, MoveLogType.FOUND),
                (PhysicalLocationClass.PLACE, VirtualLocationClass.LOST): (MoveLogType.LOST, MoveLogType.FOUND),
            }
            """Создаем MoveLog на резервирование товара, когда товар меняет одно из свойств таблицы, """
            """если движение на перемещение упаковки, то нет нужны """
            src_type, dest_type = type_map.get((src_quant.location_class, dest_quant.location_class))
            total_quantity = qty_to_move

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
                "reserved_quantity": -total_quantity,
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

    @list_brocker.task(queue_name='model')
    async def set_done(self, move: Move, sync=False):
        """
            Здесь создается mov_log, когда все саджесты выполнены
        """
        move_log_model = self.env['move_log'].model
        type_map = {
            (VirtualLocationClass.PARTNER, PhysicalLocationClass.PLACE): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
            (VirtualLocationClass.PARTNER, PhysicalLocationClass.BUFFER): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
            (PhysicalLocationClass.PLACE, PhysicalLocationClass.PLACE): (MoveLogType.PUT_OUT, MoveLogType.PUT_IN),
            (PhysicalLocationClass.PLACE, VirtualLocationClass.PARTNER): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
            (PhysicalLocationClass.PLACE, VirtualLocationClass.INVENTORY): (
                MoveLogType.INVENROTY_OUT, MoveLogType.INVENROTY_IN),
            (VirtualLocationClass.INVENTORY, PhysicalLocationClass.PLACE): (
                MoveLogType.INVENROTY_OUT, MoveLogType.INVENROTY_IN),
            (VirtualLocationClass.LOST, PhysicalLocationClass.PLACE): (MoveLogType.LOST, MoveLogType.FOUND),
            (PhysicalLocationClass.PLACE, VirtualLocationClass.LOST): (MoveLogType.LOST, MoveLogType.FOUND),
        }
        location_service = self.env['location'].service
        quant_service = self.env['quant'].service
        src_quant = await quant_service.get(move.quant_src_id)
        dest_quant = await quant_service.get(move.quant_dest_id)
        location_src = await location_service.get(move.location_src_id)
        location_dest = await location_service.get(move.location_dest_id)
        src_type, dest_type = type_map.get((location_src.location_class, location_dest.location_class))
        if move.type == 'product':
            """Создаем MoveLog только для записей, когда товар меняет одно из свойств таблицы, """
            """если движение на перемещение упаковки, то нет нужны """
            total_quantity = sum(float(s.value) for s in move.suggest_list_rel if s.type == SuggestType.IN_QUANTITY)
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
                "location_class": location_src.location_class,
                "location_id": move.location_src_id,
                "lot_id": move.lot_id if move.lot_id else None,
                "partner_id": move.partner_id if move.partner_id else None,
                "quantity": -total_quantity,
                "reserved_quantity": -total_quantity,
                "incoming_quantity": 0.0,
                "uom_id": move.uom_id,
            })
            src_quant.reserved_quantity -= total_quantity
            src_quant.quantity -= total_quantity
            self.session.add(src_quant)
            self.session.add(src_log)

            dest_log = move_log_model(**{
                "company_id": move.company_id,
                "type": dest_type,
                "order_id": move.order_id,
                "move_id": move.id,
                "product_id": move.product_id,
                "created_by": move.created_by,
                "edited_by": move.edited_by,
                "store_id": move.store_id,
                "location_class": location_dest.location_class,
                "location_id": move.location_dest_id,
                "lot_id": move.lot_id if move.lot_id else None,
                "partner_id": move.partner_id if move.partner_id else None,
                "quantity": total_quantity,
                "reserved_quantity": 0.0,
                "incoming_quantity": -total_quantity,
                "uom_id": move.uom_id,
            })
            dest_quant.incoming_quantity -= total_quantity
            dest_quant.quantity += total_quantity
            self.session.add(dest_quant)
            self.session.add(dest_log)

        move.status = MoveStatus.DONE
        return move

    @permit('move_create')
    async def create(self, obj: CreateSchemaType, parent: Order | Move | None = None, commit=True) -> ModelType:
        obj.created_by = self.user.user_id
        obj.edited_by = self.user.user_id
        return await super(MoveService, self).create(obj)

    @permit('move_delete')
    async def delete(self, id: uuid.UUID) -> None:
        if isinstance(id, uuid.UUID):
            move = await self.get(id)
            if move.status != MoveStatus.CREATED:
                raise ModuleException(status_code=406, enum=MoveErrors.WRONG_STATUS)
        return await super(MoveService, self).delete(id)

    @permit('move_move_counstructor')
    async def move_counstructor(self, move_id: uuid.UUID, moves: list) -> None:
        return await super(MoveService, self).delete(id)

    @permit('get_moves_by_barcode')
    async def get_moves_by_barcode(self, barcode: str, order_id: uuid.UUID) -> List[ModelType]:
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
