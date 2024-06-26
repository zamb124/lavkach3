import typing
import uuid

from fastapi_filter import FilterDepends

from app.bus.bus.shemas.bus_schemas import (
    BusScheme,
    BusCreateScheme,
    BusUpdateScheme,
    BusListSchema, BusFilter
)
from app.bus.bus.services import BusService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from fastapi import APIRouter, Depends, Query, Request

bus_router = APIRouter(

)


@bus_router.get("", response_model=BusListSchema)
async def bus_list(
        request: Request,
        model_filter: BusFilter = FilterDepends(BusFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await BusService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@bus_router.post("", response_model=BusScheme)
async def bus_create(request: Request, schema: BusCreateScheme):
    return await BusService(request).create(obj=schema)


@bus_router.get("/{bus_id}")
async def bus_get(request: Request, bus_id: uuid.UUID) -> typing.Union[None, BusScheme]:
    return await BusService(request).get(id=bus_id)


@bus_router.put("/{bus_id}", response_model=BusScheme)
async def bus_update(request: Request, bus_id: uuid.UUID, schema: BusUpdateScheme):
    bus_entity = await BusService(request).update(id=bus_id, obj=schema)
    return bus_entity


@bus_router.delete("/{bus_id}")
async def bus_delete(request: Request, bus_id: uuid.UUID):
    await BusService(request).delete(id=bus_id)
