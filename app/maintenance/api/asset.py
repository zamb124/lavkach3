from typing import List, Union
import uuid
from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import (
    AssetCreateScheme,
    ExceptionResponseSchema,
    AssetScheme,
    AssetUpdateScheme
)
from sqlalchemy import select, update, delete
from core.db.session import Base, session
assets_router = APIRouter()

@assets_router.get(
    "",
    response_model=List[AssetScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_assets_list(limit: int = Query(10, description="Limit")):
    return await AssetScheme.get_all(limit=limit)

@assets_router.get(
    "/{asset_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_assets(asset_id: uuid.UUID) -> Union[None, AssetScheme]:
    return await AssetScheme.get_by_id(id=asset_id)
@assets_router.post(
    "/create",
    response_model=AssetScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_assets(request: AssetCreateScheme):
    entity = await request.create()
    return entity

@assets_router.put(
    "/{asset_id}",
    response_model=AssetScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_assets(asset_id: uuid.UUID, request: AssetUpdateScheme):
    entity = await request.update(id=asset_id)
    return entity

@assets_router.delete(
    "/{asset_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_assets(asset_id: uuid.UUID):
    await AssetScheme.delete_by_id(id=asset_id)

@assets_router.get(
    "/uttils/{barcode}",
    response_model=AssetScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def search_barcode(barcode: str) -> Union[None, AssetScheme]:
    model = AssetScheme.Config.model
    query = (
        select(model)
        .where(model.barcode == barcode)
    )
    result = await session.execute(query)
    return result.scalars().first()
