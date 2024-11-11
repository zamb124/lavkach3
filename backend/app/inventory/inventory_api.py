from fastapi import APIRouter, Depends
from starlette.requests import Request

from app.inventory.inventory_service import InventoryService
from app.inventory.order.schemas import (
    ExceptionResponseSchema,
    OrderListSchema,
)
from app.inventory.schemas import CreateMovements

inventory_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@inventory_router.post("/create_movements", response_model=OrderListSchema)
async def create_movements(schema: CreateMovements, service: InventoryService = Depends()):
    await service.create_movements(schema)
    return {}
