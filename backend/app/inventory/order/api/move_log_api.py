import typing
import uuid

from fastapi import APIRouter, Query, Request, Depends
from fastapi_filter import FilterDepends

from app.inventory.order.schemas.move_log_schemas import (
    MoveLogScheme,
    MoveLogCreateScheme,
    MoveLogUpdateScheme,
    MoveLogListSchema,
    MoveLogFilter,
)
from app.inventory.order.services.move_log_service import MoveLogService

move_log_router = APIRouter()


@move_log_router.get("", response_model=MoveLogListSchema)
async def move_log_list(
        model_filter: MoveLogFilter = FilterDepends(MoveLogFilter),
        size: int = Query(ge=1, le=100, default=20),
        service: MoveLogService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@move_log_router.post("", response_model=MoveLogScheme)
async def move_log_create(schema: MoveLogCreateScheme, service: MoveLogService = Depends()):
    return await service.create(obj=schema)


@move_log_router.get("/{move_log_id}", response_model=MoveLogScheme)
async def move_log_get(move_log_id: uuid.UUID, service: MoveLogService = Depends()) -> typing.Union[
    None, MoveLogScheme]:
    return await service.get(id=move_log_id)


@move_log_router.put("/{move_log_id}", response_model=MoveLogScheme)
async def move_log_update(move_log_id: uuid.UUID, schema: MoveLogUpdateScheme, service: MoveLogService = Depends()):
    return await service.update(id=move_log_id, obj=schema)


@move_log_router.delete("/{move_log_id}")
async def move_log_delete(move_log_id: uuid.UUID, service: MoveLogService = Depends()):
    await service.delete(id=move_log_id)
