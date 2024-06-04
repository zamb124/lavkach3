import typing
import uuid

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
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from fastapi import APIRouter, Depends, Query, Request

suggest_router = APIRouter(
)


@suggest_router.get("", response_model=SuggestListSchema)
async def suggest_list(
        request: Request,
        model_filter: SuggestFilter = FilterDepends(SuggestFilter),
        size: int = Query(ge=1, le=100, default=20),
):
    data = await SuggestService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@suggest_router.post("", response_model=SuggestScheme)
async def suggest_create(request: Request, schema: SuggestCreateScheme):
    return await SuggestService(request).create(obj=schema)


@suggest_router.get("/{suggest_id}", response_model=SuggestScheme)
async def suggest_get(request: Request, suggest_id: uuid.UUID) -> typing.Union[None, SuggestScheme]:
    return await SuggestService(request).get(id=suggest_id)


@suggest_router.put("/{suggest_id}", response_model=SuggestScheme)
async def suggest_update(request: Request, suggest_id: uuid.UUID, schema: SuggestUpdateScheme):
    return await SuggestService(request).update(id=suggest_id, obj=schema)


@suggest_router.delete("/{suggest_id}")
async def suggest_delete(request: Request, suggest_id: uuid.UUID):
    await SuggestService(request).delete(id=suggest_id)

@suggest_router.post("/confirm", responses={200: {'model': list[SuggestScheme]}})
async def action_suggest_confirm(request: Request, schema: SuggestConfirmScheme):
    return await SuggestService(request).suggest_confirm(suggest_ids=schema.ids, value=schema.value)