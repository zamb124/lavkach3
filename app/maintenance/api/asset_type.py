import uuid
import typing
from fastapi import APIRouter, Query
from app.maintenance.schemas import (
    AssetTypeScheme,
    AssetTypeCreateScheme,
    AssetTypeUpdateScheme,
    ExceptionResponseSchema
)
from app.maintenance.services.maintenance import AssetTypeService

asset_type_router = APIRouter()


@asset_type_router.get(
    "",
    response_model=list[AssetTypeScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def asset_type_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Prev LSN"),
):
    return await AssetTypeService().list(limit, cursor)


@asset_type_router.post(
    "/create",
    response_model=AssetTypeScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_asset_type(request: AssetTypeCreateScheme):
    return await AssetTypeService().create(obj=request)


@asset_type_router.get(
    "/{asset_type_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_asset_type(asset_type_id: uuid.UUID) -> typing.Union[None, AssetTypeScheme]:
    return await AssetTypeService().get(id=asset_type_id)


@asset_type_router.put(
    "/{asset_type_id}",
    response_model=AssetTypeScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_asset_type(asset_type_id: uuid.UUID, request: AssetTypeUpdateScheme):
    return await AssetTypeService().update(id=asset_type_id, obj=request)


@asset_type_router.delete(
    "/{asset_type_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_asset_type(asset_type_id: uuid.UUID):
    await AssetTypeService().delete(id=asset_type_id)
