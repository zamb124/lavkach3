from typing import List, Union
import uuid
from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import (
    OrderCreateScheme,
    ExceptionResponseSchema,
    OrderScheme,
    OrderUpdateScheme,
    OrderLineCreateScheme,
    OrderLineScheme,
    OrderLineUpdateScheme,
    OrderLineInlineScheme
)

order_router = APIRouter()

@order_router.get(
    "",
    response_model=List[OrderScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_order_list(limit: int = Query(10, description="Limit")):
    return await OrderScheme.get_all(limit=limit)

@order_router.get(
    "/{order_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_order(order_id: uuid.UUID) -> Union[None, OrderScheme]:
    return await OrderScheme.get_by_id(id=order_id)
@order_router.post(
    "/create",
    response_model=OrderScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_order(request: OrderCreateScheme):
    entity = await request.create()
    return entity

@order_router.put(
    "/{order_id}",
    response_model=OrderScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_order(order_id: uuid.UUID, request: OrderUpdateScheme):
    entity = await request.update(id=order_id)
    return entity

@order_router.put(
    "/{order_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_order(order_id: uuid.UUID):
    await OrderScheme.delete_by_id(id=order_id)



#############################################
@order_router.get(
    "/line",
    response_model=List[OrderLineScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_order_line_list(limit: int = Query(10, description="Limit")):
    return await OrderLineScheme.get_all(limit=limit)

@order_router.get(
    "/line/{order_line_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_assets(order_line_id: uuid.UUID) -> Union[None, OrderLineScheme]:
    return await OrderLineScheme.get_by_id(id=order_line_id)
@order_router.post(
    "/line/create",
    response_model=OrderLineScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_order_line(request: OrderLineCreateScheme):
    entity = await request.create()
    return entity

@order_router.put(
    "/line/{order_line_id}",
    response_model=OrderLineScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_order_line(order_line_id: uuid.UUID, request: OrderLineUpdateScheme):
    entity = await request.update(id=order_line_id)
    return entity

@order_router.put(
    "/line/{order_line_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_order_line(order_line_id: uuid.UUID):
    await OrderLineScheme.delete_by_id(id=order_line_id)
