import typing
import uuid

from fastapi import APIRouter, Query, Request, Depends
from fastapi_filter import FilterDepends

from app.inventory.location.schemas import (
    LocationTypeScheme,
    LocationTypeCreateScheme,
    LocationTypeUpdateScheme,
    ExceptionResponseSchema,
    LocationTypeListSchema,
    LocationTypeFilter
)
from app.inventory.location.services import LocationTypeService

location_type_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@location_type_router.get("", response_model=LocationTypeListSchema)
async def location_list(
        model_filter: LocationTypeFilter = FilterDepends(LocationTypeFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: LocationTypeService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@location_type_router.post("", response_model=LocationTypeScheme)
async def location_create(schema: LocationTypeCreateScheme, service: LocationTypeService = Depends()):
    return await service.create(obj=schema)


@location_type_router.get("/{LocationType_id}")
async def location_get(location_type_id: uuid.UUID, service: LocationTypeService = Depends()) -> typing.Union[None, LocationTypeScheme]:
    return await service.get(id=location_type_id)


@location_type_router.put("/{location_type_id}", response_model=LocationTypeScheme)
async def location_update(location_type_id: uuid.UUID, schema: LocationTypeUpdateScheme, service: LocationTypeService = Depends()):
    return await service.update(id=location_type_id, obj=schema)


@location_type_router.delete("/{location_type_id}")
async def location_delete(location_type_id: uuid.UUID, service: LocationTypeService = Depends()):
    await service.delete(id=location_type_id)
