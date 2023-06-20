import typing
import uuid

from app.basic.store.schemas import (
    StoreScheme,
    StoreCreateScheme,
    StoreUpdateScheme,
    ExceptionResponseSchema
)
from app.basic.store.services import StoreService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from fastapi import APIRouter, Depends, Query, Request

store_router = APIRouter(
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@store_router.get("", response_model=list[StoreScheme])
async def get_store_list(request: Request, limit: int = Query(10, description="Limit"), cursor: int = Query(0, description="Cursor")):
    user = await request.user.get_user_data()
    return await StoreService().list(limit, cursor)


@store_router.post("/create", response_model=StoreScheme)
async def create_store(request: StoreCreateScheme):
    return await StoreService().create(obj=request)


@store_router.get("/{store_id}")
async def load_store(store_id: uuid.UUID) -> typing.Union[None, StoreScheme]:
    return await StoreService().get(id=store_id)


@store_router.put("/{store_id}", response_model=StoreScheme)
async def update_store(store_id: uuid.UUID, request: StoreUpdateScheme):
    return await StoreService().update(id=store_id, obj=request)


@store_router.delete(
    "/{store_id}", )
async def delete_store(store_id: uuid.UUID):
    await StoreService().delete(id=store_id)
