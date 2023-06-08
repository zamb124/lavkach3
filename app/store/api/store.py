import uuid
import typing

from fastapi import APIRouter, Depends, Query
from app.store.schemas import (
    StoreSchema,
    ExceptionResponseSchema
)
from core.repository.base import BaseRepo

store_router = APIRouter()


@store_router.post(
    "",
    response_model=list[StoreSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_store_list(limit: int = Query(10, description="Limit")):
    return await StoreSchema.get_all(limit=limit)


@store_router.post(
    "",
    response_model=StoreSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_store(request: StoreSchema):
    res = await request.create()
    return await request.get_by_id(res)


@store_router.get(
    "/{store_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_store(store_id: uuid.UUID) -> typing.Union[None, StoreSchema]:
    return await StoreSchema.get_by_id(id=store_id)
