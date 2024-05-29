import logging
import logging
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.inventory.location import Location
from app.inventory.order.models.order_models import Move, MoveType, Order, OrderType, OrderClass
from app.inventory.order.schemas.move_schemas import MoveCreateScheme, MoveUpdateScheme, MoveFilter
from app.inventory.quant import Quant
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoveService(BaseService[Move, MoveCreateScheme, MoveUpdateScheme, MoveFilter]):
    """
    Сервис для работы с Мувами
    CRUD+
    Мув нельзя создать, если запаса недостаточно (это прям правило)
    Путь мува такоф:
        CREATED:    мув создан, но уже зарезервированы кванты что бы их никто не забрал
        WAITING:    мув ждет распределение в Order - этот шаг может быть пропущен, если мув исполняют без ордера
        CONFIRMED:  мув получил Order - этот шаг может быть пропущен, если мув исполняют без ордера
        ASSIGNED:   мув взял в работу сотрудник
        DONE:       мув завершен (terminal)
        CANCELED:   мув отменен (terminal)
    """
    def __init__(self, request, db_session: AsyncSession = None):
        super(MoveService, self).__init__(request, Move, MoveCreateScheme, MoveUpdateScheme, db_session)

    @permit('move_edit')
    async def update(self, id: Any, obj: UpdateSchemaType, commit:bool =True) -> Optional[ModelType]:
        return await super(MoveService, self).update(id, obj, commit)

    @permit('move_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(MoveService, self).list(_filter, size)

    async def create_suggests(self, move):
        """
            Создаются саджесты в зависимости от OrderType и Product
        """
        if move.type == MoveType.PRODUCT:
            a=1

    @permit('move_user_assign')
    async def user_assign(self, move_id: uuid.UUID, user_id: uuid.UUID):
        """
            Если прикрепился пользователь, то значит, что необходимо создать саджесты для выполнения
        """
        move = await self.get(move_id)
        await move.create_suggests()
        move.user_id = user_id
        await self.session.commit()
        return move

    @permit('move_create')
    async def create(self, obj: CreateSchemaType, parent: Order | Move | None = None, commit=True) -> ModelType:
        """
        Входом для создания Мува может быть
         - Order - когда человек или система целенаправлено создают некий Ордер ( Ордер на примеку или Ордер на перемещение)
         - OrderType - когда Выбирается некий тип(правила) применяемые к определенному обьекту, Товарру/Упаковке
         - Move - Когда идет двуэтапное движение, тогда правила беруться из Родительского Мува
         - None - Тогда система подберет автоматически OrderType согласно подходящем

         Стратегия такова
         Если указана локация в move, то проверяется допустимость этой локации согласно правилам OrderType
         Если указан Quant, то сразу идем в Quant и фильтруем только его
         Если локация не указана, то поиск доступных квантов будет происходить в допустимых в OrderType
        """
        location_service = self.env['location'].service
        order_type_service = self.env['order_type'].service
        quant_service = self.env['quant'].service
        if obj.type == MoveType.PRODUCT:

            """ ПОДБОР ИСХОДЯЩЕГО КВАНТА/ЛОКАЦИИ"""

            quant_src_entity: Quant | None = None
            quant_dest_entity: Quant | None = None

            assert obj.product_id, 'Product is required if Move Type is  Product'
            if not obj.order_type_id:
                order_type_entity = order_type_service.get_by_attrs(**obj.model_dump()) #TODO: его надо реализовать
            elif obj.order_type_id:
                order_type_entity = await order_type_service.get(obj.order_type_id)
            elif isinstance(parent, Order):
                order_type_entity = parent.order_type_rel
            elif isinstance(parent, Move):
                order_type_entity = await order_type_service.get(parent.order_type_id)
            elif isinstance(parent, OrderType):
                order_type_entity = parent
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
            if obj.location_src_id:
                """Если мы указали локацию, то нас уже не интересуют правила из OrderType"""
                location_class_src_ids, location_type_src_ids,  location_src_ids = [], [], [obj.location_src_id,]

            available_src_quants = await quant_service.get_available_quants(
                product_id=obj.product_id,
                store_id=obj.store_id,
                id=obj.quant_src_id,
                location_class_ids=location_class_src_ids,
                location_ids=location_src_ids,
                location_type_ids=location_type_src_ids,
                lot_ids=[obj.lot_id] if obj.lot_id else None,
                partner_id=obj.partner_id if obj.partner_id else None
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
                    quant_src_entity = await quant_service.create(obj={
                        "product_id": obj.product_id,
                        "store_id": obj.store_id,
                        "location_id": loc_src.id,
                        "location_class": loc_src.location_class,
                        "location_type_id": loc_src.location_type_id,
                        "lot_id": obj.lot_id.id if obj.lot_id else None,
                        "partner_id": obj.partner_id.id if obj.partner_id else None,
                        "quantity": 0.0,
                        "reserved_quantity": 0.0,
                        "incoming_quantity": 0.0,
                        "uom_id": obj.uom_id,
                    }, commit=False)
                    available_src_quants = [quant_src_entity,]
                    break


            if available_src_quants:
                """Если кванты нашлись"""
                remainder = obj.quantity
                for src_quant in available_src_quants:
                    if obj.uom_id == src_quant.uom_id:
                        if src_quant.available_quantity <= 0.0:
                            pass
                        elif remainder <= src_quant.available_quantity:
                            src_quant.reserved_quantity += remainder
                            remainder = 0.0
                            quant_src_entity = src_quant
                            self.session.add(quant_src_entity)
                            break
                        elif remainder >= src_quant.available_quantity:
                            remainder -= src_quant.available_quantity
                            src_quant.quantity = 0.0
                            quant_src_entity = src_quant
                            self.session.add(quant_src_entity)
                            break
                    else:
                        pass#TODO: единицы измерения
                if remainder:
                    if remainder == obj.quantity:
                        "Если не нашли свободного количества вообще"
                        "снова идем по квантам и берем то, у которого локация позволяет сделать отрицательный остсток"
                        for src_quant in available_src_quants:
                            if obj.uom_id == src_quant.uom_id:
                                q_location = await location_service.get(src_quant.location_id)
                                if q_location.is_can_negative:
                                    src_quant.reserved_quantity += remainder
                                    remainder = 0.0
                                    quant_src_entity = src_quant
                                    self.session.add(quant_src_entity)
                                    break
                            else:
                                ... #TODO: единицы измерения
                    else:
                        "Если квант нашелся, но на частичное количество уменьшаем количество в муве тк 1 мув = 1квант"
                        logger.warning(f'The number in the move has been reduced')
                        obj.quantity -= remainder
            if not quant_src_entity:
                raise HTTPException(status_code=406, detail=f"It was not possible to create and find a Stock Source, perhaps the parameters were set incorrectly")

            obj.quant_src_id =      quant_src_entity.id
            obj.location_src_id =   quant_src_entity.location_id
            obj.lot_id =            quant_src_entity.lot_id
            obj.partner_id =        quant_src_entity.partner_id

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

            if obj.location_dest_id:
                """Если мы указали локацию, то нас уже не интересуют правила из OrderType"""
                location_class_dest_ids, location_type_dest_ids, location_dest_ids = [], [], [obj.location_dest_id, ]

            available_dest_quants = await quant_service.get_available_quants(
                product_id=obj.product_id,
                store_id=obj.store_id,
                id=obj.quant_dest_id,
                exclude_id=quant_src_entity.id, # Исключаем из возможного поиска квант источника, ибо нехер
                location_class_ids=location_class_dest_ids,
                location_ids=location_dest_ids,
                location_type_ids=location_type_dest_ids,
                lot_ids=[obj.lot_id] if obj.lot_id else None,
                partner_id=obj.partner_id if obj.partner_id else None
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
                    quant_dest_entity = await quant_service.create(obj={
                        "product_id": obj.product_id,
                        "store_id": obj.store_id,
                        "location_id": loc_dest.id,
                        "location_class": loc_dest.location_class,
                        "location_type_id": loc_dest.location_type_id,
                        "lot_id": obj.lot_id.id if obj.lot_id else None,
                        "partner_id": obj.partner_id.id if obj.partner_id else None,
                        "quantity": 0.0,
                        "reserved_quantity": 0.0,
                        "incoming_quantity": 0.0,
                        "uom_id": obj.uom_id,
                    }, commit=False)
                    available_dest_quants = [quant_dest_entity, ]
                    break

            for dest_quant in available_dest_quants:
                quant_dest_entity = dest_quant
                quant_dest_entity.incoming_quantity += obj.quantity
                self.session.add(quant_dest_entity)
                break
            if not quant_dest_entity:
                raise HTTPException(status_code=406, detail=f"It was not possible to create and find a Stock Dest, perhaps the parameters were set incorrectly")

            obj.quant_dest_id =      quant_dest_entity.id
            obj.location_dest_id =   quant_dest_entity.location_id

            if quant_src_entity == quant_dest_entity:
                raise HTTPException(status_code=406, detail=f"Source Quant and Destination Quant cannot be the same")

            move = await super(MoveService, self).create(obj, commit=False)
            if not quant_src_entity.move_ids:
                quant_src_entity.move_ids = [move.id]
            else:
                quant_src_entity.move_ids.append(move.id)

            if not quant_dest_entity.move_ids:
                quant_dest_entity.move_ids = [move.id]
            else:
                quant_dest_entity.move_ids.append(move.id)

            try:
                await self.session.commit()
                await self.session.refresh(move)
            except Exception as ex:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail=f"ERROR:  {str(ex)}")
            return move

    @permit('move_delete')
    async def delete(self, id: Any) -> None:
        return await super(MoveService, self).delete(id)


    @permit('move_move_counstructor')
    async def move_counstructor(self, move_id: uuid.UUID, moves: list) -> None:
        return await super(MoveService, self).delete(id)
