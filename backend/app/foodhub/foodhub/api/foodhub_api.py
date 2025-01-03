import typing
import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from app.foodhub.foodhub.schemas import (
    PrescriptionScheme,
    PrescriptionCreateScheme,
    PrescriptionUpdateScheme,
    ExceptionResponseSchema, PrescriptionListSchema, PrescriptionFilter
)
from app.foodhub.foodhub.services import PrescriptionService

prescription_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@prescription_router.get("", response_model=PrescriptionListSchema)
async def prescription_list(
        model_filter: PrescriptionFilter = FilterDepends(PrescriptionFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: PrescriptionService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@prescription_router.post("", response_model=PrescriptionScheme)
async def prescription_create(schema: PrescriptionCreateScheme,
                              service: PrescriptionService = Depends()):
    return await service.create(obj=schema)


@prescription_router.get("/{prescription_id}")
async def prescription_get(prescription_id: uuid.UUID, service: PrescriptionService = Depends()) -> \
typing.Union[
    None, PrescriptionScheme]:
    return await service.get(id=prescription_id)


@prescription_router.put("/{prescription_id}", response_model=PrescriptionScheme)
async def prescription_update(prescription_id: uuid.UUID, schema: PrescriptionUpdateScheme,
                              service: PrescriptionService = Depends()):
    return await service.update(id=prescription_id, obj=schema)


@prescription_router.delete("/{prescription_id}")
async def prescription_delete(prescription_id: uuid.UUID, service: PrescriptionService = Depends()):
    await service.delete(id=prescription_id)
