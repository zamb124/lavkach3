import logging
import logging
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.inventory.order.models.order_models import Move, MoveType, Order, OrderType, OrderClass
from app.inventory.order.schemas.move_schemas import MoveCreateScheme, MoveUpdateScheme, MoveFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoveService(BaseService[Move, MoveCreateScheme, MoveUpdateScheme, MoveFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(MoveService, self).__init__(request, Move, MoveCreateScheme, MoveUpdateScheme, db_session)

    @permit('move_edit')
    async def update(self, id: Any, obj: UpdateSchemaType, commit:bool =True) -> Optional[ModelType]:
        return await super(MoveService, self).update(id, obj, commit)

    @permit('move_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(MoveService, self).list(_filter, size)

    @permit('move_create')
    async def create(self, obj: CreateSchemaType, parent: Order | Move = None, commit=True) -> ModelType:
        """
        Входом для создания Мува может быть
         - Order - когда человек или система целенаправлено создают некий Ордер ( Ордер на примеку или Ордер на перемещение)
         - OrderType - когда Выбирается некий тип(правила) применяемые к определенному обьекту, Товарру/Упаковке
         - Move - Когда идет двуэтапное движение, тогда правила беруться из Родительского Мува
         - None - Тогда система подберет автоматически OrderType согласно стратегии размещения

         Стратегия такова
         Если указана локация в move, то проверяется допустимость этой локации согласно правилам OrderType
         Если локация не указана, то поиск доступных квантов будет происходить в допустимых в OrderType
        """
        if obj.type == MoveType.PRODUCT:

            """ ПОДБОР ИСХОДЯЩЕГО КВАНТА/ЛОКАЦИИ"""

            quant_src_entity = None
            available_quants = None
            assert obj.product_id, 'Product is required if Move Type is  Product'
            if obj.order_type_id:
                order_type_entity = await self.env['order_type'].service.get(obj.order_type_id)
            elif isinstance(parent, Order):
                order_type_entity = parent.order_type_rel
            elif isinstance(parent, Move):
                order_type_entity = await self.env['order_type'].service.get(parent.order_type_id)
            elif isinstance(parent, OrderType):
                order_type_entity = parent
            """Проверяем, что мув может быть создан согласно праавилам в Order type """
            quant_service = self.env['quant'].service
            if obj.location_src_id:
                """Если указали локацию насильно, то нужно проверить все что возможно, что эта локация имеет место быть"""
                if order_type_entity.allowed_location_src_ids:
                    """Если есть разрешенные локации"""
                    if not obj.location_src_id in order_type_entity.allowed_location_src_ids:
                        raise HTTPException(
                            status_code=406,
                            detail=f"Source Location is not allowed for Order Type {order_type_entity.title}"
                        )
                if order_type_entity.exclude_location_src_ids:
                    """Если есть разрешенные локации"""
                    if not obj.location_src_id in order_type_entity.exclude_location_src_ids:
                        raise HTTPException(
                            status_code=406,
                            detail=f"Source Location is not allowed for Order Type {order_type_entity.title}"
                        )
                loc_env = self.env['location']
                location_entity = await loc_env.service.get(obj.location_src_id)
                if order_type_entity.allowed_location_type_src_ids:
                    """Если есть исключающие локации"""
                    if location_entity.location_type_id in order_type_entity.allowed_location_type_src_ids:
                        raise HTTPException(
                            status_code=406,
                            detail=f"Source Location Type is not allowed for Order Type {parent.order_type_rel.title}"
                        )
                if order_type_entity.exclude_location_type_src_ids:
                    """Если есть исключающие локации"""
                    if location_entity.location_type_id in order_type_entity.exclude_location_type_src_ids:
                        raise HTTPException(
                            status_code=406,
                            detail=f"Source Location Type is not allowed for Order Type {parent.order_type_rel.title}"
                        )
                if order_type_entity.allowed_location_class_src_ids:
                    """Еслли есть правила разрешаюшее по классу"""
                    if not location_entity.location_class in order_type_entity.allowed_location_class_src_ids:
                        raise HTTPException(
                            status_code=406,
                            detail=f"Source Location class is not allowed for Order Type Location Type {order_type_entity.title}"
                        )
                if order_type_entity.exclude_location_class_src_ids:
                    """Еслли есть правила разрешаюшее по типу локации"""
                    if location_entity.location_class in order_type_entity.exclude_location_class_src_ids:
                        raise HTTPException(
                            status_code=406,
                            detail=f"Source Location Type is not allowed for Order Type Location Type {order_type_entity.title}"
                        )
                """Далее нужно достать доступные кванты товара для создания движения"""
                available_quants = await quant_service.get_available_quants(
                    product_id=obj.product_id,
                    store_id=obj.store_id,
                    location_class_ids=[location_entity.location_class],
                    location_ids=[obj.location_src_id],
                    location_type_ids=[location_entity.location_type_id],
                    lot_ids=[obj.lot_id],
                    partner_id=obj.partner_id
                )
                if not available_quants:
                    if location_entity.location_type_id:
                        location_type = await self.env['location_type'].service.get(location_entity.location_type_id)
                        if location_type.is_can_negative:
                            quant_src_entity = await self.env['quant'].service.create(obj = {
                            "product_id": obj.product_id,
                            "store_id": obj.store_id,
                            "location_id": obj.location_src_id,
                            "location_class": location_entity.location_class,
                            "location_type_id": location_entity.location_type_id,
                            "lot_id": obj.lot_id,
                            "partner_id": obj.partner_id,
                            "quantity": 0.0,
                            "reserved_quantity": obj.quantity,
                            "uom_id": obj.uom_id,
                            }, commit=False)
                        else:
                            raise HTTPException(status_code=406, detail='Not enouth quantity in source')
            else:
                "Если локации в задании нет, то подбираем локацию из правила OrderType"

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
                available_quants = await quant_service.get_available_quants(
                    product_id=obj.product_id,
                    store_id=obj.store_id,
                    location_class_ids=location_class_src_ids,
                    location_ids=location_src_ids,
                    location_type_ids=location_type_src_ids,
                    lot_ids=[obj.lot_id] if obj.lot_id else None,
                    partner_id=obj.partner_id
                )
                if not available_quants:
                    if order_type_entity.order_class == OrderClass.INCOMING:
                        """Если ничего не нашлось, то идем по пути поиска локаций с отрицательными остатками"""
                        """Если класс ордера INCOMING и локейшен, или тип локации или класс локации Допустим к отрицательным остаткам"""
                        if location_src_ids:
                            "Если указана локация, то она в приоритете на изьятия кванта"
                            location_env = self.env['location']
                            locations_src = await location_env.service.list(_filter={'id__in': location_src_ids})
                            location_types_ids = {i.id: i.location_type_id for i in locations_src}
                            location_types_src = {
                                i.id: i
                                for i in await self.env['location_type'].service.list(_filter={'id__in': location_types_ids.values()})
                            }
                            for location in locations_src:
                                if loc_type := location_types_src.get(location.location_type_id):
                                    if loc_type.is_can_negative:
                                        quant_src_entity = await self.env['quant'].service.create(obj={
                                            "product_id": obj.product_id,
                                            "store_id": obj.store_id,
                                            "location_id": location.id,
                                            "location_class": location.location_class,
                                            "location_type_id": loc_type.id,
                                            "lot_id": obj.lot_id.id if obj.lot_id else None,
                                            "partner_id": obj.partner_id.id if obj.partner_id else None,
                                            "quantity": 0.0,
                                            "reserved_quantity": obj.quantity,
                                            "uom_id": obj.uom_id,
                                        }, commit=False)
                        elif location_type_src_ids:
                            """Если нет локации ищем по типу локации с подходящим c возможностью отрицательного остатка"""
                            location_type_src_entities = await self.env['location_type'].service.list(_filter={'id__in': location_type_src_ids})
                            location_type_src_is_can_negative = {i.id: i for i in location_type_src_entities if i.is_can_negative}
                            location_env = self.env['location']
                            location = await location_env.service.list(_filter={'location_type_id__in': location_type_src_is_can_negative.keys()}, size=1)
                            if location:
                                quant_src_entity = await self.env['quant'].service.create(obj={
                                    "product_id": obj.product_id,
                                    "store_id": obj.store_id,
                                    "location_id": location[0].id,
                                    "location_class": location[0].location_class,
                                    "location_type_id": location_type_src_is_can_negative.get(location[0].location_type_id).id,
                                    "lot_id": obj.lot_id.id if obj.lot_id else None,
                                    "partner_id": obj.partner_id.id if obj.partner_id else None,
                                    "quantity": 0.0,
                                    "reserved_quantity": obj.quantity,
                                    "uom_id": obj.uom_id,
                                }, commit=False)

                        elif location_class_src_ids:
                            """Если нет локации  ищем по классу локации с подходящим c возможностью отрицательного остатка"""
                            location_type_src_entities = await self.env['location_type'].service.list(_filter={'location_class__in': location_class_src_ids})
                            location_type_src_is_can_negative = {i.id: i for i in location_type_src_entities if i.is_can_negative}
                            location_env = self.env['location']
                            location = await location_env.service.list(
                                _filter={'location_type_id__in': location_type_src_is_can_negative.keys()}, size=1)
                            if location:
                                quant_src_entity = await self.env['quant'].service.create(obj={
                                    "product_id": obj.product_id,
                                    "store_id": obj.store_id,
                                    "location_id": location[0].id,
                                    "location_class": location[0].location_class,
                                    "location_type_id": location_type_src_is_can_negative.get(location[0].location_type_id).id,
                                    "lot_id": obj.lot_id.id if obj.lot_id else None,
                                    "partner_id": obj.partner_id.id if obj.partner_id else None,
                                    "quantity": 0.0,
                                    "reserved_quantity": obj.quantity,
                                    "uom_id": obj.uom_id,
                                }, commit=False)
                        else:
                            raise HTTPException(status_code=406, detail='Not enouth quantity in source')


                    elif order_type_entity.order_class == OrderClass.OUTGOING:
                        ...
                    elif order_type_entity.order_class == OrderClass.INTERNAL:
                        ...
                    if not quant_src_entity:
                        raise HTTPException(status_code=406, detail='Not enouth quantity in source')
            if available_quants:
                """Если кванты нашлись"""
                remainder = obj.quantity
                for q in available_quants:
                    if obj.uom_id == q.uom_id:
                        if q.available_quantity <= 0.0:
                            pass
                        elif remainder <= q.available_quantity:
                            remainder = 0.0
                            q.reserved_quantity += remainder
                            break
                        elif remainder >= q.available_quantity:
                            remainder -= q.quantity
                            q.quantity = 0.0
                            self.session.add(q)
                    else:
                        pass#TODO: единицы измерения
                if remainder:
                    if remainder == obj.quantity:
                        "Если не нашли свободного количества вообще"
                        "снова идем по квантам и берем то, у которого локация позволяет сделать отрицательный остсток"
                        for q in available_quants:
                            if obj.uom_id == q.uom_id:
                                quant_location_type = await self.env['location_type'].service.get(q.location_type_id)
                                if quant_location_type.is_can_negative:
                                    q.reserved_quantity += remainder
                                    remainder = 0.0
                                    quant_src_entity = q
                                    self.session.add(quant_src_entity)
                                    break
                            else:
                                ... #TODO: единицы измерения
                    else:
                        "Если квант нашелся, но на частичное количество уменьшаем количество в муве тк 1 мув = 1квант"
                        logger.warning(f'The number in the move has been reduced')
                        obj.quantity -= remainder

            obj.quant_src_id =      quant_src_entity.id
            obj.location_src_id =   quant_src_entity.location_id
            obj.lot_id =            quant_src_entity.lot_id
            obj.partner_id =        quant_src_entity.partner_id

            """ ПОИСК КВАНТА/ЛОКАЦИИ НАЗНАЧЕНИЯ """
            if obj.location_dest_id:
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

            move = await super(MoveService, self).create(obj, commit=False)
            if not quant_src_entity.move_ids:
                quant_src_entity.move_ids = [move.id]
            else:
                quant_src_entity.move_ids.append(move.id)

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
