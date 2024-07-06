import typing
import uuid

from fastapi import APIRouter, Query, Request, Depends
from fastapi_filter import FilterDepends

from app.inventory.order.schemas.move_schemas import (
    MoveScheme,
    MoveCreateScheme,
    MoveUpdateScheme,
    MoveListSchema,
    MoveFilter, MoveConfirmScheme,
)
from app.inventory.order.services.move_service import MoveService

move_router = APIRouter(

)


@move_router.get("", response_model=MoveListSchema)
async def move_list(
        model_filter: MoveFilter = FilterDepends(MoveFilter),
        size: int = Query(ge=1, le=100, default=20),
        service: MoveService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@move_router.post("", response_model=MoveScheme)
async def move_create(schema: MoveCreateScheme, service: MoveService = Depends()):
    return await service.create(obj=schema)


@move_router.get("/{move_id}", response_model=MoveScheme)
async def move_get(move_id: uuid.UUID, service: MoveService = Depends()) -> typing.Union[None, MoveScheme]:
    return await service.get(id=move_id)


@move_router.put("/{move_id}", response_model=MoveScheme)
async def move_update(move_id: uuid.UUID, schema: MoveUpdateScheme, service: MoveService = Depends()):
    return await service.update(id=move_id, obj=schema)


@move_router.delete("/{move_id}")
async def move_delete(move_id: uuid.UUID, service: MoveService = Depends()):
    await service.delete(id=move_id)


@move_router.post("/confirm")
async def action_move_confirm(schema: MoveConfirmScheme, service: MoveService = Depends()):
    return await service.confirm(moves=schema.ids)
