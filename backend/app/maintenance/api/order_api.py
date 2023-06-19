import typing
import uuid

from fastapi import APIRouter, Depends, Query

from app.maintenance.schemas import (
    OrderScheme,
    OrderCreateScheme,
    OrderUpdateScheme,
    ExceptionResponseSchema,

    OrderLineScheme,
    OrderLineCreateScheme,
    OrderLineUpdateScheme
)
from app.maintenance.services.maintenance_service import OrderLineService
from app.maintenance.services.maintenance_service import OrderService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

order_router = APIRouter(
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@order_router.get("", response_model=list[OrderScheme])
async def asset_order(limit: int = Query(10, description="Limit"), cursor: int = Query(0, description="Prev LSN")):
    return await OrderService().list(limit, cursor)


@order_router.post("/create", response_model=OrderScheme)
async def create_order(request: OrderCreateScheme):
    return await OrderService().create(obj=request)


@order_router.get("/{order_id}")
async def load_order(order_id: uuid.UUID) -> typing.Union[None, OrderScheme]:
    return await OrderService().get(id=order_id)


@order_router.put("/{order_id}", response_model=OrderScheme)
async def update_order(order_id: uuid.UUID, request: OrderUpdateScheme):
    return await OrderService().update(id=order_id, obj=request)


@order_router.delete("/{order_id}")
async def delete_order(order_id: uuid.UUID):
    await OrderService().delete(id=order_id)


#########################################

@order_router.get("/line", response_model=list[OrderLineScheme])
async def asset_order_line(limit: int = Query(10, description="Limit"), cursor: int = Query(0, description="Prev LSN")):
    return await OrderLineService().list(limit, cursor)


@order_router.post("/line/create", response_model=OrderLineScheme)
async def create_order_line(request: OrderLineCreateScheme):
    return await OrderLineService().create(obj=request)


@order_router.get("/line/{order_line_id}")
async def load_order_line(order_line_id: uuid.UUID) -> typing.Union[None, OrderLineScheme]:
    return await OrderLineService().get(id=order_line_id)


@order_router.put("/line/{order_line_id}", response_model=OrderLineScheme)
async def update_order_line(order_line_id: uuid.UUID, request: OrderLineUpdateScheme):
    return await OrderLineService().update(id=order_line_id, obj=request)


@order_router.delete("/line/{order_line_id}")
async def delete_order_line(order_line_id: uuid.UUID):
    await OrderLineService().delete(id=order_line_id)
