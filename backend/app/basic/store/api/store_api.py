import typing
import uuid

from fastapi import APIRouter, Query, Request, Depends
from fastapi_filter import FilterDepends

from app.basic.store.schemas import (
    StoreScheme,
    StoreCreateScheme,
    StoreUpdateScheme,
    ExceptionResponseSchema, StoreListSchema, StoreFilter
)
from app.basic.store.services import StoreService
from core.schemas.basic_schemes import ActionBaseSchame, ActionRescposeSchema

store_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@store_router.get("", response_model=StoreListSchema)
async def store_list(
        model_filter: StoreFilter = FilterDepends(StoreFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: StoreService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@store_router.post("", response_model=StoreScheme)
async def store_create(schema: StoreCreateScheme, service: StoreService = Depends()):
    return await service.create(obj=schema)


@store_router.get("/{store_id}")
async def store_get(store_id: uuid.UUID, service: StoreService = Depends()) -> typing.Union[
    None, StoreScheme]:
    return await service.get(id=store_id)


@store_router.put("/{store_id}", response_model=StoreScheme)
async def store_update(store_id: uuid.UUID, schema: StoreUpdateScheme,
                       service: StoreService = Depends()):
    return await service.update(id=store_id, obj=schema)


@store_router.delete("/{store_id}")
async def store_delete(store_id: uuid.UUID, service: StoreService = Depends()):
    await service.delete(id=store_id)


@store_router.post("/assign_store", response_model=ActionRescposeSchema)
async def assign_store(schema: ActionBaseSchame, service: StoreService = Depends()):
    return await service.assign_store(store_id=schema.ids[0])
