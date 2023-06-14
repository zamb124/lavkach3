import typing
import uuid

from fastapi import APIRouter, Depends, Query

from app.maintenance.schemas import (
    AssetTypeScheme,
    AssetTypeCreateScheme,
    AssetTypeUpdateScheme,
    ExceptionResponseSchema
)
from app.maintenance.services.maintenance_service import AssetLogService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

asset_log_router = APIRouter(
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@asset_log_router.get("", response_model=list[AssetTypeScheme])
async def asset_log_list(limit: int = Query(10, description="Limit"), cursor: int = Query(0, description="Prev LSN"), ):
    return await AssetLogService().list(limit, cursor)


@asset_log_router.post("/create", response_model=AssetTypeScheme)
async def create_asset_log(request: AssetTypeCreateScheme):
    return await AssetLogService().create(obj=request)


@asset_log_router.get("/{asset_log_id}")
async def load_asset_log(asset_log_id: uuid.UUID) -> typing.Union[None, AssetTypeScheme]:
    return await AssetLogService().get(id=asset_log_id)


@asset_log_router.put("/{asset_log_id}", response_model=AssetTypeScheme)
async def update_asset_log(asset_log_id: uuid.UUID, request: AssetTypeUpdateScheme):
    return await AssetLogService().update(id=asset_log_id, obj=request)


@asset_log_router.delete("/{asset_log_id}")
async def delete_asset_log(asset_log_id: uuid.UUID):
    await AssetLogService().delete(id=asset_log_id)
