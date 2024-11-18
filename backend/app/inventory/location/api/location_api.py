import typing
import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from app.inventory.location.schemas import (
    LocationScheme,
    LocationCreateScheme,
    LocationUpdateScheme,
    ExceptionResponseSchema,
    LocationListSchema,
    LocationFilter
)
from app.inventory.location.services import LocationService

location_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@location_router.get("", response_model=LocationListSchema)
async def location_list(
        model_filter: LocationFilter = FilterDepends(LocationFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: LocationService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}

@location_router.post("", response_model=LocationScheme)
async def location_create(schema: LocationCreateScheme, service: LocationService = Depends()):
    return await service.create(obj=schema)


@location_router.get("/{Location_id}")
async def location_get(location_id: uuid.UUID, service: LocationService = Depends()) -> typing.Union[None, LocationScheme]:
    return await service.get(id=location_id)


@location_router.put("/{location_id}", response_model=LocationScheme)
async def location_update(location_id: uuid.UUID, schema: LocationUpdateScheme, service: LocationService = Depends()):
    return await service.update(id=location_id, obj=schema)


@location_router.delete("/{location_id}")
async def location_delete(location_id: uuid.UUID, service: LocationService = Depends()):
    await service.delete(id=location_id)
