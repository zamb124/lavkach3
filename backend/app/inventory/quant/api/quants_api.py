import uuid

from fastapi import APIRouter, Query, Depends
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
    responses={"400": {"model": ExceptionResponseSchema}},
)


@quant_router.get("", response_model=QuantListSchema)
async def quant_list(
        model_filter: QuantFilter = FilterDepends(QuantFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: QuantService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@quant_router.post("", response_model=QuantScheme)
async def quant_create(schema: QuantCreateScheme, service: QuantService = Depends()):
    return await service.create(obj=schema)


@quant_router.get("/{quant_id}", response_model=QuantScheme)
async def quant_get(quant_id: uuid.UUID, service: QuantService = Depends()):
    return await service.get(id=quant_id)


@quant_router.put("/{quant_id}", response_model=QuantScheme)
async def quant_update(quant_id: uuid.UUID, schema: QuantUpdateScheme, service: QuantService = Depends()):
    return await service.update(id=quant_id, obj=schema)


@quant_router.delete("/{quant_id}")
async def quant_delete(quant_id: uuid.UUID, service: QuantService = Depends()):
    await service.delete(id=quant_id)
