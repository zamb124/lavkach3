from __future__ import annotations
import typing
import uuid

from fastapi import APIRouter, Query, Request
from fastapi_filter import FilterDepends

from app.basic.product.schemas import (
    ProductScheme,
    ProductCreateScheme,
    ProductUpdateScheme,
    ProductListSchema,
    ProductFilter,
    ExceptionResponseSchema,
)
from app.basic.product.services import ProductService

product_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@product_router.get("", response_model=ProductListSchema)
async def product_list(
        request: Request,
        model_filter: ProductFilter = FilterDepends(ProductFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await ProductService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@product_router.post("", response_model=ProductScheme)
async def product_create(request: Request, schema: ProductCreateScheme):
    return await ProductService(request).create(obj=schema)


@product_router.get("/{product_id}")
async def product_get(request: Request, product_id: uuid.UUID) -> typing.Union[None, ProductScheme]:
    return await ProductService(request).get(id=product_id)


@product_router.put("/{product_id}", response_model=ProductScheme)
async def product_update(request: Request, product_id: uuid.UUID, schema: ProductUpdateScheme):
    return await ProductService(request).update(id=product_id, obj=schema)


@product_router.delete("/{product_id}")
async def product_delete(request: Request, product_id: uuid.UUID):
    await ProductService(request).delete(id=product_id)
