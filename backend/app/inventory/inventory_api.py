from fastapi import APIRouter, Depends

from app.inventory.order import MoveService
from app.inventory.order.schemas import (
    ExceptionResponseSchema,
)
from app.inventory.schemas import CreateMovements

inventory_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@inventory_router.post("/create_movements", response_model=CreateMovements)
async def create_movements(schema: CreateMovements, service: MoveService = Depends()):
    res = await service.create_movements(schema)
    return res
