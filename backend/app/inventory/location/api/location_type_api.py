import typing
import uuid

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
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from fastapi import APIRouter, Depends, Query, Request

location_type_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@location_type_router.get("", response_model=LocationTypeListSchema)
async def location_list(
        request: Request,
        model_filter: LocationTypeFilter = FilterDepends(LocationTypeFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await LocationTypeService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@location_type_router.post("", response_model=LocationTypeScheme)
async def location_create(request: Request, schema: LocationTypeCreateScheme):
    return await LocationTypeService(request).create(obj=schema)


@location_type_router.get("/{LocationType_id}")
async def location_get(request: Request, location_type_id: uuid.UUID) -> typing.Union[None, LocationTypeScheme]:
    return await LocationTypeService(request).get(id=location_type_id)


@location_type_router.put("/{location_type_id}", response_model=LocationTypeScheme)
async def location_update(request: Request, location_type_id: uuid.UUID, schema: LocationTypeUpdateScheme):
    return await LocationTypeService(request).update(id=location_type_id, obj=schema)


@location_type_router.delete("/{location_type_id}")
async def location_delete(request: Request, location_type_id: uuid.UUID):
    await LocationTypeService(request).delete(id=location_type_id)
