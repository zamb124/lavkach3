import typing
import uuid

from fastapi import APIRouter, Query, Request
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
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@store_router.get("", response_model=StoreListSchema)
async def store_list(
        request: Request,
        model_filter: StoreFilter = FilterDepends(StoreFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await StoreService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@store_router.post("", response_model=StoreScheme)
async def store_create(request: Request, schema: StoreCreateScheme):
    return await StoreService(request).create(obj=schema)


@store_router.get("/{store_id}")
async def store_get(request: Request, store_id: uuid.UUID) -> typing.Union[None, StoreScheme]:
    return await StoreService(request).get(id=store_id)


@store_router.put("/{store_id}", response_model=StoreScheme)
async def store_update(request: Request, store_id: uuid.UUID, schema: StoreUpdateScheme):
    store_entity = await StoreService(request).update(id=store_id, obj=schema)
    return store_entity


@store_router.delete("/{store_id}")
async def store_delete(request: Request, store_id: uuid.UUID):
    await StoreService(request).delete(id=store_id)


@store_router.post("/assign_store", response_model=ActionRescposeSchema)
async def assign_store(request: Request, schema: ActionBaseSchame):
    return await StoreService(request).assign_store(store_id=schema.ids[0])
