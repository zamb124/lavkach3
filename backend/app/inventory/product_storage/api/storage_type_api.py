import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from app.inventory.product_storage.schemas import (
    StorageTypeScheme,
    StorageTypeCreateScheme,
    StorageTypeUpdateScheme,
    StorageTypeListSchema,
    StorageTypeFilter,
    ExceptionResponseSchema,
)
from app.inventory.product_storage.services import StorageTypeService

storage_type_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@storage_type_router.get("", response_model=StorageTypeListSchema)
async def storage_type_list(
        model_filter: StorageTypeFilter = FilterDepends(StorageTypeFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: StorageTypeService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@storage_type_router.post("", response_model=StorageTypeScheme)
async def storage_type_create(schema: StorageTypeCreateScheme,service: StorageTypeService = Depends()):
    return await service.create(obj=schema)


@storage_type_router.get("/{storage_type_id}")
async def storage_type_get(storage_type_id: uuid.UUID, service: StorageTypeService = Depends()):
    return await service.get(id=storage_type_id)


@storage_type_router.put("/{storage_type_id}", response_model=StorageTypeScheme)
async def storage_type_update(storage_type_id: uuid.UUID, schema: StorageTypeUpdateScheme,service: StorageTypeService = Depends()):
    return await service.update(id=storage_type_id, obj=schema)


@storage_type_router.delete("/{storage_type_id}")
async def storage_type_delete(storage_type_id: uuid.UUID,
                              service: StorageTypeService = Depends()):
    await service.delete(id=storage_type_id)
