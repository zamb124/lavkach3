import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends
from pydantic.v1 import UUID4

from app.inventory.order.schemas import (
    OrderScheme,
    OrderCreateScheme,
    OrderUpdateScheme,
    ExceptionResponseSchema,
    OrderListSchema,
    OrderFilter,
)
from app.inventory.order.schemas.order_schemas import AssignUser, OrderConfirm, OrderComplete, OrderStart
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


@order_router.post("/order_assign", response_model=OrderScheme)
async def order_assign(schema: AssignUser, service: OrderService = Depends()):
    return await service.order_assign(order_id=schema.id, user_id=schema.user_id)


@order_router.post("/order_confirm", response_model=list[OrderScheme])
async def order_confirm(schema: OrderConfirm, service: OrderService = Depends()):
    return await service.order_confirm(order_id=schema.id)


@order_router.post("/order_start", response_model=list[OrderScheme])
async def order_start(schema: OrderStart, service: OrderService = Depends()):
    return await service.order_start(order_id=schema.id)


@order_router.post("/order_complete", response_model=list[OrderScheme])
async def order_complete(schema: OrderComplete, service: OrderService = Depends()):
    return await service.order_complete(order_id=schema.id)
