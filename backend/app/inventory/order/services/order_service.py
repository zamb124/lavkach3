import datetime
import uuid
from typing import Any, Optional, List
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.order.enums.order_enum import OrderStatus
from app.inventory.order.models.order_models import Order
from app.inventory.order.schemas.order_schemas import OrderCreateScheme, OrderUpdateScheme, OrderFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class OrderService(BaseService[Order, OrderCreateScheme, OrderUpdateScheme, OrderFilter]):
    def __init__(self, request: Request):
        super(OrderService, self).__init__(request, Order, OrderCreateScheme, OrderUpdateScheme)

    @permit('order_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(OrderService, self).update(id, obj)

    @permit('order_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(OrderService, self).list(_filter, size)

    @permit('order_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        """
            Метод создания ордера, в нем особой проверки не нужно, тк в теории ордер может быть создан как угодно
        """
        obj.number = datetime.datetime.now(datetime.UTC).strftime('%y%m%d%H%m%S')
        obj.created_by = self.user.user_id
        obj.edited_by = self.user.user_id
        return await super(OrderService, self).create(obj)

    @permit('order_delete')
    async def delete(self, id: Any) -> None:
        return await super(OrderService, self).delete(id)


    @permit('order_move_counstructor')
    async def move_counstructor(self, order_id: uuid.UUID, moves: list) -> None:
        return await super(OrderService, self).delete(id)

    @permit('assign_order')
    async def assign_order(self, order_id: uuid.UUID, user_id: uuid.UUID = None) -> ModelType:
        order_entity = await self.get(order_id)
        if user_id:
            order_entity.user_ids.append(user_id)
        else:
            order_entity.user_ids.append(self.user.user_id)
        await self.session.commit()
        await self.session.refresh(order_entity)
        await order_entity.notify('update')
        return order_entity

    @permit('order_start')
    async def order_start(self, ids: List[uuid.UUID], user_id: uuid.UUID = None) -> List[ModelType]:
        """ Стартует ордера, конфермит все мувы и ставит статус Confirmed"""
        res = []
        for order_id in ids:
            order_entity = await self.get(order_id)
            for move in order_entity.move_list_rel:
                await self.env['move'].service._confirm(move=move)
            if user_id:
                order_entity.user_ids.append(user_id)
            else:
                order_entity.user_ids.append(self.user.user_id)
            order_entity.status = OrderStatus.CONFIRMED
            await self.session.commit()
            await self.session.refresh(order_entity)
            await order_entity.notify('update')
            for move in order_entity.move_list_rel:
                await self.session.refresh(move)
            res.append(order_entity)
        return res

