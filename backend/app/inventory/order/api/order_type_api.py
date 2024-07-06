import typing
import uuid

from fastapi import APIRouter, Query, Request, Depends
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
    responses={"400": {"model": ExceptionResponseSchema}},
)

@order_type_router.get("", response_model=OrderTypeListSchema)
async def order_type_list(
        model_filter: OrderTypeFilter = FilterDepends(OrderTypeFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: OrderTypeService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@order_type_router.post("", response_model=OrderTypeScheme)
async def order_type_create(schema: OrderTypeCreateScheme, service: OrderTypeService = Depends()):
    return await service.create(obj=schema)


@order_type_router.get("/{order_type_id}")
async def order_type_get(order_type_id: uuid.UUID, service: OrderTypeService = Depends()) -> typing.Union[None, OrderTypeScheme]:
    return await service.get(id=order_type_id)


@order_type_router.put("/{order_type_id}", response_model=OrderTypeScheme)
async def order_type_update(order_type_id: uuid.UUID, schema: OrderTypeUpdateScheme, service: OrderTypeService = Depends()):
    return await service.update(id=order_type_id, obj=schema)


@order_type_router.delete("/{order_type_id}")
async def order_type_delete(order_type_id: uuid.UUID, service: OrderTypeService = Depends()):
    await service.delete(id=order_type_id)
