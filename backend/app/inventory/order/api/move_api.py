import typing
import uuid

from fastapi_filter import FilterDepends

from app.inventory.order.schemas.move_schemas import (
    MoveScheme,
    MoveCreateScheme,
    MoveUpdateScheme,
    MoveListSchema,
    MoveFilter,
)
from app.inventory.order.services.move_service import MoveService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from fastapi import APIRouter, Depends, Query, Request

move_router = APIRouter(
)


@move_router.get("", response_model=MoveListSchema)
async def move_list(
        request: Request,
        model_filter: MoveFilter = FilterDepends(MoveFilter),
        size: int = Query(ge=1, le=100, default=20),
):
    data = await MoveService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@move_router.post("", response_model=MoveScheme)
async def Move_create(request: Request, schema: MoveCreateScheme):
    return await MoveService(request).create(obj=schema)


@move_router.get("/{move_id}", response_model=MoveScheme)
async def Move_get(request: Request, move_id: uuid.UUID) -> typing.Union[None, MoveScheme]:
    return await MoveService(request).get(id=move_id)


@move_router.put("/{move_id}", response_model=MoveScheme)
async def Move_update(request: Request, move_id: uuid.UUID, schema: MoveUpdateScheme):
    return await MoveService(request).update(id=move_id, obj=schema)


@move_router.delete("/{move_id}")
async def Move_delete(request: Request, move_id: uuid.UUID):
    await MoveService(request).delete(id=move_id)
