import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from app.inventory.product_storage.schemas import (
    ProductStorageTypeScheme,
    ProductStorageTypeCreateScheme,
    ProductStorageTypeUpdateScheme,
    ProductStorageTypeListSchema,
    ProductStorageTypeFilter,
    ExceptionResponseSchema,
)
from app.inventory.product_storage.services import ProductStorageTypeService

product_storage_type_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@product_storage_type_router.get("", response_model=ProductStorageTypeListSchema)
async def product_storage_type_list(
        model_filter: ProductStorageTypeFilter = FilterDepends(ProductStorageTypeFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: ProductStorageTypeService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@product_storage_type_router.post("", response_model=ProductStorageTypeScheme)
async def product_storage_type_create(schema: ProductStorageTypeCreateScheme,
                                      service: ProductStorageTypeService = Depends()):
    return await service.create(obj=schema)


@product_storage_type_router.get("/{product_storage_type_id}")
async def product_storage_type_get(product_storage_type_id: uuid.UUID, service: ProductStorageTypeService = Depends()):
    return await service.get(id=product_storage_type_id)


@product_storage_type_router.put("/{product_storage_type_id}", response_model=ProductStorageTypeScheme)
async def product_storage_type_update(product_storage_type_id: uuid.UUID, schema: ProductStorageTypeUpdateScheme,
                                      service: ProductStorageTypeService = Depends()):
    return await service.update(id=product_storage_type_id, obj=schema)


@product_storage_type_router.delete("/{product_storage_type_id}")
async def product_storage_type_delete(product_storage_type_id: uuid.UUID,
                                      service: ProductStorageTypeService = Depends()):
    await service.delete(id=product_storage_type_id)
