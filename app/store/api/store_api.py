import uuid
import typing
from fastapi import APIRouter, Query
from app.store.schemas import (
    StoreScheme,
    StoreCreateScheme,
    StoreUpdateScheme,
    ExceptionResponseSchema
)
from app.store.services import StoreService

store_router = APIRouter()


@store_router.get(
    "",
    response_model=list[StoreScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_store_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Prev LSN"),
):
    return await StoreService().list(limit, cursor)


@store_router.post(
    "/create",
    response_model=StoreScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_store(request: StoreCreateScheme):
    return await StoreService().create(obj=request)


@store_router.get(
    "/{store_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_store(store_id: uuid.UUID) -> typing.Union[None, StoreScheme]:
    return await StoreService().get(id=store_id)


@store_router.put(
    "/{store_id}",
    response_model=StoreScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_store(store_id: uuid.UUID, request: StoreUpdateScheme):
    return await StoreService().update(id=store_id, obj=request)


@store_router.delete(
    "/{store_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_store(store_id: uuid.UUID):
    await StoreService().delete(id=store_id)
