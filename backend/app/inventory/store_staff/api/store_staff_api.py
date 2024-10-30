import typing
import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from app.inventory.store_staff.schemas import (
    StoreStaffScheme,
    StoreStaffCreateScheme,
    StoreStaffUpdateScheme,
    ExceptionResponseSchema,
    StoreStaffListSchema,
    StoreStaffFilter
)
from app.inventory.store_staff.services import StoreStaffService

store_staff_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@store_staff_router.get("", response_model=StoreStaffListSchema)
async def store_staff_list(
        model_filter: StoreStaffFilter = FilterDepends(StoreStaffFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: StoreStaffService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@store_staff_router.post("", response_model=StoreStaffScheme)
async def store_staff_create(schema: StoreStaffCreateScheme, service: StoreStaffService = Depends()):
    return await service.create(obj=schema)


@store_staff_router.get("/{store_staff_id}")
async def store_staff_get(store_staff_id: uuid.UUID, service: StoreStaffService = Depends()) -> typing.Union[
    None, StoreStaffScheme]:
    return await service.get(id=store_staff_id)


@store_staff_router.put("/{store_staff_id}", response_model=StoreStaffScheme)
async def store_staff_update(store_staff_id: uuid.UUID, schema: StoreStaffUpdateScheme,
                             service: StoreStaffService = Depends()):
    return await service.update(id=store_staff_id, obj=schema)


@store_staff_router.delete("/{store_staff_id}")
async def store_staff_delete(store_staff_id: uuid.UUID, service: StoreStaffService = Depends()):
    await service.delete(id=store_staff_id)
