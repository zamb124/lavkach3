import uuid
import typing

from fastapi import APIRouter, Query, HTTPException
from app.store.schemas import (
    StoreSchema,
    ExceptionResponseSchema,
)
from core.integration.wms import ClientWMS

store_router = APIRouter()


@store_router.get(
    "",
    response_model=list[StoreSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_store_list(limit: int = Query(10, description="Limit")):
    return await StoreSchema.get_all(limit=limit)


@store_router.post(
    "/create",
    response_model=StoreSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_store(request: StoreSchema):
    res = await request.create()
    return res


@store_router.get(
    "/{store_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_store(store_id: uuid.UUID) -> typing.Union[None, StoreSchema]:
    return await StoreSchema.get_by_id(id=store_id)


@store_router.post(
    "/sync",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def sync_stores(token):
    response = await ClientWMS.req(cursor=None, path='/api/external/stores/v1/list', token=token)

    if response is None:
        raise HTTPException(status_code=403, detail='Wrong token')

    for store in response['stores']:
        store = StoreSchema(
            title=store['title'],
            external_id=store['store_id'],
            address=store['address'] or 'no adress',
            source='wms',
        )
        try:
            await store.create()
        except Exception:
            continue

    return {'code': 'OK'}
