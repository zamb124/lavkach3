import datetime
import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.inventory.order.models.order_models import Move, MoveType, Order
from app.inventory.order.schemas.move_schemas import MoveCreateScheme, MoveUpdateScheme, MoveFilter
from core.db import Transactional
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType



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
    async def create(self, obj: CreateSchemaType, parent: Order | Move, commit=True) -> ModelType:
        """
        Создание мува, здесь важно проверить все
        1 - Проверить, что тип ордера не противоречит правилам локаций
        2 - Проверить всю хурму в общем
        """
        assert parent, 'You cannot create a move without a parent Order'
        if isinstance(parent, Order):
            order = parent
        if isinstance(parent, Move):
            order = parent.order_id
        """Проверяем, что мув может быть создан согласно праавилам в Order type """
        quant_service = self.env['quant'].service
        if obj.location_src_id:
            """Если указали локацию насильно, то нужно проверить все что возможно, что эта локация имеет место быть"""
            if parent.order_type_rel.allowed_location_src_ids:
                """Если есть разрешенные локации"""
                if not obj.location_src_id in parent.order_type_rel.allowed_location_src_ids:
                    raise HTTPException(
                        status_code=406,
                        detail=f"Source Location is not allowed for Order Type {parent.order_type_rel.title}"
                    )
            if parent.order_type_rel.exclude_location_src_ids:
                """Если есть исключающие локации"""
                if obj.location_src_id in parent.order_type_rel.exclude_location_src_ids:
                    raise HTTPException(
                        status_code=406,
                        detail=f"Source Location is not allowed for Order Type {parent.order_type_rel.title}"
                    )
            loc_env = self.env['location']
            location_entity = await loc_env.service.get(obj.location_src_id)
            if parent.order_type_rel.allowed_location_type_ids:
                """Еслли есть правила разрешаюшее по типу локации"""
                if not location_entity.location_type_id in parent.order_type_rel.allowed_location_type_ids:
                    raise HTTPException(
                        status_code=406,
                        detail=f"Source Location Type is not allowed for Order Type Location Type {parent.order_type_rel.title}"
                    )
            if parent.order_type_rel.exclude_location_type_ids:
                """Еслли есть правила разрешаюшее по типу локации"""
                if location_entity.location_type_id in parent.order_type_rel.exclude_location_type_ids:
                    raise HTTPException(
                        status_code=406,
                        detail=f"Source Location Type is not allowed for Order Type Location Type {parent.order_type_rel.title}"
                    )

            if parent.order_type_rel.allowed_location_classes:
                """Еслли есть правила разрешаюшее по классу локации"""
                if not location_entity.location_class in parent.order_type_rel.allowed_location_classes:
                    raise HTTPException(
                        status_code=406,
                        detail=f"Source Location Class is not allowed for Order Type Location Class {parent.order_type_rel.title}"
                    )
            if parent.order_type_rel.exclude_location_classes:
                """Еслли есть правила разрешаюшее по классу локации"""
                if  location_entity.location_class in parent.order_type_rel.exclude_location_classes:
                    raise HTTPException(
                        status_code=406,
                        detail=f"Source Location Class is not allowed for Order Type Location Class {parent.order_type_rel.title}"
                    )
            """Далее нужно достать доступные кванты товара для создания движения"""
            available_quants = await quant_service.get_available_quants(
                order_type=order.order_type_rel,
                product_id=obj.product_id,
                package=obj.location_id,
                uom_id=obj.uom_id,
                location=location_entity,
                lot=order.lot_id,
                partner_id=order.partner_id
            )
            if not available_quants:
                if location_entity.location_type_id:
                    location_type = await self.env['location_type'].service.get(location_entity.location_type_id)
                    if location_type.is_can_negative:
                        quant_entity = await self.env['quant'].service.create(obj = {
                        "product_id": obj.product_id,
                        "store_id":order.store_id,
                        "location_id": location_entity.id,
                        "lot_id": order.lot_id,
                        "partner_id": order.partner_id,
                        "quantity": 0.0,
                        "reserved_quantity": obj.quantity,
                        "uom_id": obj.uom_id,
                        }, commit=False)
                    else:
                        raise HTTPException(status_code=406, detail='Not enouth quantity in source')
            else:
                remainder = obj.quantity
                for q in available_quants:
                    if obj.uom_id == q.uom_id:
                        if q.quantity <= 0.0:
                            pass
                        elif remainder <= q.quantity:
                            remainder = 0.0
                            q.reserved_quantity += remainder
                            break
                        elif remainder >= q.quantity:
                            remainder -= q.quantity
                            q.quantity = 0.0
                            self.session.add(q)
                    else:
                        pass
                if remainder:
                    pass
        else:
            available_quants = await quant_service.get_available_quants(
                order_type=order.order_type_rel,
                product_id=obj.product_id,
                package=obj.location_id,
                uom_id=obj.uom_id,
                lot=order.lot_id,
                partner_id=order.partner_id
            )
        move =  await super(MoveService, self).create(obj, commit=False)
        try:
            await self.session.commit()
            await self.session.refresh(move)
        except Exception as ex:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        return move

    @permit('move_delete')
    async def delete(self, id: Any) -> None:
        return await super(MoveService, self).delete(id)


    @permit('move_move_counstructor')
    async def move_counstructor(self, move_id: uuid.UUID, moves: list) -> None:
        return await super(MoveService, self).delete(id)
