import uuid
import typing
from fastapi import APIRouter, Query
from app.maintenance.schemas import (
    AssetScheme,
    AssetCreateScheme,
    AssetUpdateScheme,
    ExceptionResponseSchema
)
from app.maintenance.services.maintenance_service import AssetService

asset_router = APIRouter()


@asset_router.get(
    "",
    response_model=list[AssetScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def asset_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Prev LSN"),
):
    return await AssetService().list(limit, cursor)


@asset_router.post(
    "/create",
    response_model=AssetScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_asset(request: AssetCreateScheme):
    return await AssetService().create(obj=request)


@asset_router.get(
    "/{asset_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_asset(asset_id: uuid.UUID) -> typing.Union[None, AssetScheme]:
    return await AssetService().get(id=asset_id)


@asset_router.put(
    "/{asset_id}",
    response_model=AssetScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_asset(asset_id: uuid.UUID, request: AssetUpdateScheme):
    return await AssetService().update(id=asset_id, obj=request)


@asset_router.delete(
    "/{asset_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_asset(asset_id: uuid.UUID):
    await AssetService().delete(id=asset_id)
