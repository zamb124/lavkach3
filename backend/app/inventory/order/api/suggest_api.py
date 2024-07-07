import typing
import uuid

from fastapi import APIRouter, Query, Request, Depends
from fastapi_filter import FilterDepends

from app.inventory.order.schemas.suggest_schemas import (
    SuggestScheme,
    SuggestCreateScheme,
    SuggestUpdateScheme,
    SuggestListSchema,
    SuggestFilter,
    SuggestConfirmScheme
)
from app.inventory.order.services.suggest_service import SuggestService

suggest_router = APIRouter(
)


@suggest_router.get("", response_model=SuggestListSchema)
async def suggest_list(
        model_filter: SuggestFilter = FilterDepends(SuggestFilter),
        size: int = Query(ge=1, le=100, default=20),
        service: SuggestService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@suggest_router.post("", response_model=SuggestScheme)
async def suggest_create(schema: SuggestCreateScheme, service: SuggestService = Depends()):
    return await service.create(obj=schema)


@suggest_router.get("/{suggest_id}", response_model=SuggestScheme)
async def suggest_get(suggest_id: uuid.UUID, service: SuggestService = Depends()) -> typing.Union[None, SuggestScheme]:
    return await service.get(id=suggest_id)


@suggest_router.put("/{suggest_id}", response_model=SuggestScheme)
async def suggest_update(suggest_id: uuid.UUID, schema: SuggestUpdateScheme, service: SuggestService = Depends()):
    return await service.update(id=suggest_id, obj=schema)


@suggest_router.delete("/{suggest_id}")
async def suggest_delete(suggest_id: uuid.UUID, service: SuggestService = Depends()):
    await service.delete(id=suggest_id)

@suggest_router.post("/confirm", responses={200: {'model': list[SuggestScheme]}})
async def action_suggest_confirm(schema: SuggestConfirmScheme, service: SuggestService = Depends()):
    return await service.suggest_confirm(suggest_ids=schema.ids, value=schema.value)
