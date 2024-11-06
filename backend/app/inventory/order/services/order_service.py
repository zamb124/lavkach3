import asyncio
import datetime
import uuid
from typing import Any, Optional, List

from fastapi import HTTPException
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.order.enums.order_enum import OrderStatus
from app.inventory.order.models.order_models import Order
from app.inventory.order.schemas.order_schemas import OrderCreateScheme, OrderUpdateScheme, OrderFilter
from core.exceptions.module import ModuleException
from core.helpers.broker.tkq import list_brocker
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


@list_brocker.task
async def print_foo(foo: str = None) -> None:
    env = list_brocker.state.data['env'].get_env()
    adapter = env['order'].adapter
    service = env['order'].service
    some_order = await service.list({'lsn__gt': 0})
    order = await adapter.get(some_order[0].id)
    await asyncio.sleep(3)
    print(foo)


class OrderService(BaseService[Order, OrderCreateScheme, OrderUpdateScheme, OrderFilter]):
    def __init__(self, request: Request):
        super(OrderService, self).__init__(request, Order, OrderCreateScheme, OrderUpdateScheme)

    @permit('order_update')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(OrderService, self).update(id, obj)

    @permit('order_list')
    async def list(self, _filter: FilterSchemaType, size: int = 100):
        return await super(OrderService, self).list(_filter, size)

    @permit('order_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        """
            Метод создания ордера, в нем особой проверки не нужно, тк в теории ордер может быть создан как угодно
        """
        obj.number = datetime.datetime.now(datetime.UTC).strftime('%y%m%d%H%m%S')
        obj.created_by = self.user.user_id
        obj.edited_by = self.user.user_id
        await print_foo.kiq('sd')
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
            new_users = set(order_entity.user_ids)
            order_entity.user_ids = list(new_users)
        else:
            order_entity.user_ids.append(self.user.user_id)
        await self.session.commit()
        await self.session.refresh(order_entity)
        await order_entity.notify('update')
        return order_entity

    @permit('order_start')
    async def order_start(self, ids: List[uuid.UUID], user_id: uuid.UUID) -> List[ModelType]:
        """Ставим статус CONFIRMING и запускаем процесс подтверждения по каждому таску"""
        res = []
        for order_id in ids:
            try:
                order_entity = await self.get(order_id, for_update=True)
                if order_entity.status != OrderStatus.CREATED:
                    raise HTTPException(status_code=401, detail=f"Order {order_entity.number} is not in CREATED status")
                move_ids = [move.id for move in order_entity.move_list_rel]
                '''Отправляем таски по каждому муву'''
                await self.env['move'].service.confirm.kiq(None, move_ids=move_ids, user_id=user_id)
                order_entity.status = OrderStatus.CONFIRMING
                await self.session.commit()
                await self.session.refresh(order_entity)
            except Exception as ex:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail=f"ERROR:  {str(ex)}")
            await order_entity.notify('update')
        return res
