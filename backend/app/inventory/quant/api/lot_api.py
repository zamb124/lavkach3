import uuid

from fastapi import APIRouter, Query, Request
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
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@lot_router.get("", response_model=LotListSchema)
async def lot_list(
        request: Request,
        model_filter: LotFilter = FilterDepends(LotFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await LotService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@lot_router.post("/create", response_model=LotScheme)
async def lot_create(request: Request, schema: LotCreateScheme):
    return await LotService(request).create(obj=schema)


@lot_router.get("/{lot_id}", response_model=LotScheme)
async def lot_get(request: Request, lot_id: uuid.UUID):
    return await LotService(request).get(id=lot_id)


@lot_router.put("/{lot_id}", response_model=LotScheme)
async def lot_update(request: Request, lot_id: uuid.UUID, schema: LotUpdateScheme):
    return await LotService(request).update(id=lot_id, obj=schema)


@lot_router.delete("/{lot_id}")
async def lot_delete(request: Request, lot_id: uuid.UUID):
    await LotService(request).delete(id=lot_id)
