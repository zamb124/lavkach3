import typing
import uuid

from fastapi import APIRouter, Depends, Query

from app.maintenance.schemas import (
    AssetScheme,
    AssetCreateScheme,
    AssetUpdateScheme,
    ExceptionResponseSchema
)
from app.maintenance.services.maintenance_service import AssetService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

asset_router = APIRouter(
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@asset_router.get("",response_model=list[AssetScheme])
async def asset_list(limit: int = Query(10, description="Limit"),cursor: int = Query(0, description="Prev LSN"),):
    return await AssetService().list(limit, cursor)


@asset_router.post("/create",response_model=AssetScheme)
async def create_asset(request: AssetCreateScheme):
    return await AssetService().create(obj=request)


@asset_router.get("/{asset_id}")
async def load_asset(asset_id: uuid.UUID) -> typing.Union[None, AssetScheme]:
    return await AssetService().get(id=asset_id)


@asset_router.put("/{asset_id}",response_model=AssetScheme)
async def update_asset(asset_id: uuid.UUID, request: AssetUpdateScheme):
    return await AssetService().update(id=asset_id, obj=request)


@asset_router.delete("/{asset_id}")
async def delete_asset(asset_id: uuid.UUID):
    await AssetService().delete(id=asset_id)
