import uuid

from fastapi import APIRouter, Query, Request
from fastapi_filter import FilterDepends

from app.inventory.quant.schemas import (
    QuantScheme,
    QuantCreateScheme,
    QuantUpdateScheme,
    ExceptionResponseSchema,
    QuantListSchema,
    QuantFilter
)
from app.inventory.quant.services import QuantService

quant_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@quant_router.get("", response_model=QuantListSchema)
async def quant_list(
        request: Request,
        model_filter: QuantFilter = FilterDepends(QuantFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await QuantService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@quant_router.post("", response_model=QuantScheme)
async def quant_create(request: Request, schema: QuantCreateScheme):
    return await QuantService(request).create(obj=schema)


@quant_router.get("/{quant_id}", response_model=QuantScheme)
async def quant_get(request: Request, quant_id: uuid.UUID):
    return await QuantService(request).get(id=quant_id)


@quant_router.put("/{quant_id}", response_model=QuantScheme)
async def quant_update(request: Request, quant_id: uuid.UUID, schema: QuantUpdateScheme):
    return await QuantService(request).update(id=quant_id, obj=schema)


@quant_router.delete("/{quant_id}")
async def quant_delete(request: Request, quant_id: uuid.UUID):
    await QuantService(request).delete(id=quant_id)
