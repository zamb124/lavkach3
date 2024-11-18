import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from app.inventory.quant.schemas import (
    LotScheme,
    LotCreateScheme,
    LotUpdateScheme,
    ExceptionResponseSchema,
    LotListSchema,
    LotFilter
)
from app.inventory.quant.services import LotService

lot_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@lot_router.get("", response_model=LotListSchema)
async def lot_list(
        model_filter: LotFilter = FilterDepends(LotFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: LotService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@lot_router.post("", response_model=LotScheme)
async def lot_create(schema: LotCreateScheme, service: LotService = Depends()):
    return await service.create(obj=schema)


@lot_router.get("/{lot_id}", response_model=LotScheme)
async def lot_get(lot_id: uuid.UUID, service: LotService = Depends()):
    return await service.get(id=lot_id)


@lot_router.put("/{lot_id}", response_model=LotScheme)
async def lot_update(lot_id: uuid.UUID, schema: LotUpdateScheme, service: LotService = Depends()):
    return await service.update(id=lot_id, obj=schema)


@lot_router.delete("/{lot_id}")
async def lot_delete(lot_id: uuid.UUID, service: LotService = Depends()):
    await service.delete(id=lot_id)
