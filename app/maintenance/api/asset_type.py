from typing import List, Union
import uuid
from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import (
    AssetTypeCreateScheme,
    ExceptionResponseSchema,
    AssetTypeScheme,
    AssetTypeUpdateScheme
)

assets_type_router = APIRouter()

@assets_type_router.post(
    "",
    response_model=List[AssetTypeScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_assets_type_list(limit: int = Query(10, description="Limit")):
    return await AssetTypeScheme.get_all(limit=limit)

@assets_type_router.get(
    "/{asset_type_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_assets_type(asset_type_id: uuid.UUID) -> Union[None, AssetTypeScheme]:
    return await AssetTypeScheme.get_by_id(id=asset_type_id)
@assets_type_router.post(
    "/create",
    response_model=AssetTypeScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_assets_type(request: AssetTypeCreateScheme):
    entity = await request.create()
    return entity

@assets_type_router.put(
    "/{asset_type_id}",
    response_model=AssetTypeScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_assets_type(asset_type_id: uuid.UUID, request: AssetTypeUpdateScheme):
    entity = await request.update(id=asset_type_id)
    return entity

@assets_type_router.delete(
    "/{asset_type_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_assets_type(asset_type_id: uuid.UUID):
    await AssetTypeScheme.delete_by_id(id=asset_type_id)
