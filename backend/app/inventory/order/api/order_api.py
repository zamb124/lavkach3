import typing
import uuid

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
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from fastapi import APIRouter, Depends, Query, Request

order_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@order_router.get("", response_model=OrderListSchema)
async def order_list(
        request: Request,
        model_filter: OrderFilter = FilterDepends(OrderFilter),
        size: int = Query(ge=1, le=100, default=20),
):
    data = await OrderService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@order_router.post("", response_model=OrderScheme)
async def order_create(request: Request, schema: OrderCreateScheme):
    return await OrderService(request).create(obj=schema)


@order_router.get("/{order_id}")
async def order_get(request: Request, order_id: uuid.UUID) -> typing.Union[None, OrderScheme]:
    return await OrderService(request).get(id=order_id)


@order_router.put("/{order_id}", response_model=OrderScheme)
async def order_update(request: Request, order_id: uuid.UUID, schema: OrderUpdateScheme):
    return await OrderService(request).update(id=order_id, obj=schema)


@order_router.delete("/{order_id}")
async def order_delete(request: Request, order_id: uuid.UUID):
    await OrderService(request).delete(id=order_id)
