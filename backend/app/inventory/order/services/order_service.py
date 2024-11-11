import asyncio
import datetime
import logging
import traceback
import uuid
from typing import Any, Optional, List

from fastapi import HTTPException
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.order.enums.exceptions_move_enums import MoveErrors, OrderErrors
from app.inventory.order.enums.order_enum import OrderStatus, MoveStatus
from app.inventory.order.models.order_models import Order
from app.inventory.order.schemas.order_schemas import OrderCreateScheme, OrderUpdateScheme, OrderFilter
from core.exceptions.module import ModuleException
from core.helpers.broker.tkq import list_brocker
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    @permit('order_assign')
    async def order_assign(self, order_id: uuid.UUID, user_id: uuid.UUID = None) -> ModelType:
        order_entity = await self.get(order_id)
        if user_id:
            order_entity.user_ids.append(user_id)
            new_users = set(order_entity.user_ids)
            order_entity.user_ids = list(new_users)
        else:
            order_entity.user_ids.append(self.user.user_id)
        if order_entity.status == OrderStatus.WAITING:
            order_entity.status = OrderStatus.PROCESSING
        await self.session.commit()
        await self.session.refresh(order_entity)
        move_ids = set(move.id for move in order_entity.move_list_rel)
        # Если есть мувы и есть саджесты и Статус ордера (ОЖИДАЕТ), то создаем саджесты
        for move in order_entity.move_list_rel:
            if move.suggest_list_rel:
                move_ids.discard(move.id)
        await self.env['move'].service.create_suggests.kiq(None, move_ids=move_ids, user_id=user_id)
        await order_entity.notify('update')
        return order_entity

    @permit('order_confirm')
    async def order_confirm(self, ids: List[uuid.UUID], user_id: uuid.UUID) -> List[ModelType]:
        """Ставим статус CONFIRMING и запускаем процесс подтверждения по каждому таску"""
        res = []
        for order_id in ids:
            try:
                order_entity = await self.get(order_id, for_update=True)
                if order_entity.status not in (OrderStatus.CREATED, OrderStatus.RESERVATION_FAILED, OrderStatus.CONFIRMING):
                    raise ModuleException(status_code=406, enum=OrderErrors.WRONG_STATUS)
                for move in order_entity.move_list_rel:
                    if not move.status in (MoveStatus.CREATED, MoveStatus.RESERVATION_FAILED, MoveStatus.CONFIRMING):
                        raise ModuleException(status_code=406, enum=MoveErrors.WRONG_STATUS)
                    move.status = MoveStatus.CONFIRMING
                move_ids = [move.id for move in order_entity.move_list_rel]
                '''Отправляем таску на подтверждение мувов'''
                await self.env['move'].service.confirm.kiq(None, move_ids=move_ids, user_id=user_id)
                order_entity.status = OrderStatus.CONFIRMING
                await self.session.commit()
                await self.session.refresh(order_entity)
            except Exception as e:
                await self.session.rollback()
                logging.error("Произошла ошибка: %s", e)
                logging.error("Трейсбек ошибки:\n%s", traceback.format_exc())
                raise e
            await order_entity.notify('update')
        return res

    @permit('order_start')
    async def order_start(self, ids: List[uuid.UUID], user_id: uuid.UUID) -> List[ModelType]:
        """Ставим статус CONFIRMING и запускаем процесс подтверждения по каждому таску"""
        res = []
        for order_id in ids:
            try:
                order_entity = await self.get(order_id, for_update=True)
                if order_entity.status != OrderStatus.CONFIRMED:
                    raise ModuleException(status_code=406, enum=OrderErrors.WRONG_STATUS)
                for move in order_entity.move_list_rel:
                    if move.status != MoveStatus.CONFIRMED:
                        raise ModuleException(status_code=406, enum=MoveErrors.WRONG_STATUS)
                    move.status = MoveStatus.WAITING
                order_entity.status = OrderStatus.WAITING
                await self.session.commit()
                await self.session.refresh(order_entity)
            except Exception as e:
                await self.session.rollback()
                logging.error("Произошла ошибка: %s", e)
                logging.error("Трейсбек ошибки:\n%s", traceback.format_exc())
                raise e
            await order_entity.notify('update')
        return res

    @permit('order_complete')
    async def order_complete(self, ids: List[uuid.UUID], user_id: uuid.UUID) -> list:
        """Ставим статус DONE"""
        res = []
        for order_id in ids:
            try:
                order_entity = await self.get(order_id, for_update=True)
                if order_entity.status != OrderStatus.PROCESSING:
                    raise ModuleException(
                        status_code=406,
                        enum=OrderErrors.WRONG_STATUS,
                        message='Order is not in PROCESSING status',
                        args={'status': order_entity.status}
                    )
                for move in order_entity.move_list_rel:
                    if move.status != MoveStatus.DONE:
                       """ Пытаемся синхронно завершить все мувы"""
                       task = await self.env['move'].service.set_done.kiq(None, move_id=move.id, user_id=self.user.user_id)
                       result = await task.wait_result(timeout=5)
                       if result.error:
                           raise ModuleException(
                                status_code=406,
                                enum=MoveErrors.WRONG_STATUS,
                                message=f'Move {move.id} is not in DONE status',
                                args={'status': move.status}
                            )
                order_entity.status = OrderStatus.DONE
                await self.session.commit()
                await self.session.refresh(order_entity)
            except Exception as e:
                await self.session.rollback()
                logging.error("Произошла ошибка: %s", e)
                logging.error("Трейсбек ошибки:\n%s", traceback.format_exc())
                raise e
            await order_entity.notify('update')
        return res