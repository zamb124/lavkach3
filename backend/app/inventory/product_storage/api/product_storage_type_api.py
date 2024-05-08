import typing
import uuid

from fastapi import APIRouter, Query, Request
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
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@product_storage_type_router.get("", response_model=ProductStorageTypeListSchema)
async def product_storage_type_list(
        request: Request,
        model_filter: ProductStorageTypeFilter = FilterDepends(ProductStorageTypeFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await ProductStorageTypeService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@product_storage_type_router.post("", response_model=ProductStorageTypeScheme)
async def product_storage_type_create(request: Request, schema: ProductStorageTypeCreateScheme):
    return await ProductStorageTypeService(request).create(obj=schema)


@product_storage_type_router.get("/{product_storage_type_id}")
async def product_storage_type_get(request: Request, product_storage_type_id: uuid.UUID) -> typing.Union[None, ProductStorageTypeScheme]:
    return await ProductStorageTypeService(request).get(id=product_storage_type_id)


@product_storage_type_router.put("/{product_storage_type_id}", response_model=ProductStorageTypeScheme)
async def product_storage_type_update(request: Request, product_storage_type_id: uuid.UUID, schema: ProductStorageTypeUpdateScheme):
    return await ProductStorageTypeService(request).update(id=product_storage_type_id, obj=schema)


@product_storage_type_router.delete("/{product_storage_type_id}")
async def product_storage_type_delete(request: Request, product_storage_type_id: uuid.UUID):
    await ProductStorageTypeService(request).delete(id=product_storage_type_id)
