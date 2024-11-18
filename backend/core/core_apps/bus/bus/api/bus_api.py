import typing
import uuid

from fastapi import APIRouter, Depends, Query
from fastapi_filter import FilterDepends

from ...bus.services import BusService
from ...bus.shemas.bus_schemas import (
    BusScheme,
    BusCreateScheme,
    BusUpdateScheme,
    BusListSchema, BusFilter
)

bus_router = APIRouter(

)


@bus_router.get("", response_model=BusListSchema)
async def bus_list(

        model_filter: BusFilter = FilterDepends(BusFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: BusService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@bus_router.post("", response_model=BusScheme)
async def bus_create(schema: BusCreateScheme, service: BusService = Depends()):
    return await service.create(obj=schema)


@bus_router.get("/{bus_id}")
async def bus_get(bus_id: uuid.UUID, service: BusService = Depends()) -> typing.Union[None, BusScheme]:
    return await service.get(id=bus_id)


@bus_router.put("/{bus_id}", response_model=BusScheme)
async def bus_update(bus_id: uuid.UUID, schema: BusUpdateScheme, service: BusService = Depends()):
    bus_entity = await service.update(id=bus_id, obj=schema)
    return bus_entity


@bus_router.delete("/{bus_id}")
async def bus_delete(bus_id: uuid.UUID, service: BusService = Depends()):
    await service.delete(id=bus_id)

@bus_router.get("/utils/active_connections")
async def get_active_connections(service: BusService = Depends()):
    res = await service.get_active_connections()
    return res
