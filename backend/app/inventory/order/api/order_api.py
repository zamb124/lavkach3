import typing
import uuid

from fastapi import APIRouter, Query, Request, Depends
from fastapi_filter import FilterDepends

from app.inventory.order.schemas import (
    OrderScheme,
    OrderCreateScheme,
    OrderUpdateScheme,
    ExceptionResponseSchema,
    OrderListSchema,
    OrderFilter,
)
from app.inventory.order.services import OrderService

order_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@order_router.get("", response_model=OrderListSchema)
async def order_list(
        model_filter: OrderFilter = FilterDepends(OrderFilter),
        size: int = Query(ge=1, le=100, default=20),
        service: OrderService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@order_router.post("", response_model=OrderScheme)
async def order_create(schema: OrderCreateScheme, service: OrderService = Depends()):
    return await service.create(obj=schema)


@order_router.get("/{order_id}")
async def order_get(order_id: uuid.UUID, service: OrderService = Depends()):
    return await service.get(id=order_id)


@order_router.put("/{order_id}", response_model=OrderScheme)
async def order_update(order_id: uuid.UUID, schema: OrderUpdateScheme, service: OrderService = Depends()):
    return await service.update(id=order_id, obj=schema)


@order_router.delete("/{order_id}")
async def order_delete(order_id: uuid.UUID, service: OrderService = Depends()):
    await service.delete(id=order_id)
