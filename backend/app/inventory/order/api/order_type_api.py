import typing
import uuid

from fastapi import APIRouter, Query, Request
from fastapi_filter import FilterDepends

from app.inventory.order.schemas import (
    ExceptionResponseSchema,
    OrderTypeScheme,
    OrderTypeUpdateScheme,
    OrderTypeCreateScheme,
    OrderTypeListSchema,
    OrderTypeFilter,

)
from app.inventory.order.services import OrderTypeService

order_type_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)

@order_type_router.get("", response_model=OrderTypeListSchema)
async def order_type_list(
        request: Request,
        model_filter: OrderTypeFilter = FilterDepends(OrderTypeFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await OrderTypeService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@order_type_router.post("", response_model=OrderTypeScheme)
async def order_type_create(request: Request, schema: OrderTypeCreateScheme):
    return await OrderTypeService(request).create(obj=schema)


@order_type_router.get("/{order_type_id}")
async def order_type_get(request: Request, order_type_id: uuid.UUID) -> typing.Union[None, OrderTypeScheme]:
    return await OrderTypeService(request).get(id=order_type_id)


@order_type_router.put("/{order_type_id}", response_model=OrderTypeScheme)
async def order_type_update(request: Request, order_type_id: uuid.UUID, schema: OrderTypeUpdateScheme):
    return await OrderTypeService(request).update(id=order_type_id, obj=schema)


@order_type_router.delete("/{order_type_id}")
async def order_type_delete(request: Request, order_type_id: uuid.UUID):
    await OrderTypeService(request).delete(id=order_type_id)
