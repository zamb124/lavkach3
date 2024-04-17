import typing
import uuid

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
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from fastapi import APIRouter, Depends, Query, Request

location_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@location_router.get("", response_model=LocationListSchema)
async def location_list(
        request: Request,
        model_filter: LocationFilter = FilterDepends(LocationFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await LocationService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}

@location_router.post("", response_model=LocationScheme)
async def location_create(request: Request, schema: LocationCreateScheme):
    return await LocationService(request).create(obj=schema)


@location_router.get("/{Location_id}")
async def location_get(request: Request, location_id: uuid.UUID) -> typing.Union[None, LocationScheme]:
    return await LocationService(request).get(id=location_id)


@location_router.put("/{location_id}", response_model=LocationScheme)
async def location_update(request: Request, location_id: uuid.UUID, schema: LocationUpdateScheme):
    return await LocationService(request).update(id=location_id, obj=schema)


@location_router.delete("/{location_id}")
async def location_delete(request: Request, location_id: uuid.UUID):
    await LocationService(request).delete(id=location_id)
