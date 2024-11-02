from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends
from starlette.requests import Request

from app.inventory.order.schemas import (
    ExceptionResponseSchema,
    OrderListSchema,
    OrderFilter,
)
from app.inventory.order.services import OrderService

inventory_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@inventory_router.get("/store_monitor", response_model=OrderListSchema)
async def store_monitor(request: Request):
    return {'size': len(data), 'cursor': cursor, 'data': data}