from __future__ import annotations

import typing
import uuid

from fastapi import APIRouter, Query, Depends
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
    responses={"400": {"model": ExceptionResponseSchema}},
)


@product_router.get("", response_model=ProductListSchema)
async def product_list(
        model_filter: ProductFilter = FilterDepends(ProductFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: ProductService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@product_router.post("", response_model=ProductScheme)
async def product_create(schema: ProductCreateScheme, service: ProductService = Depends()):
    return await service.create(obj=schema)


@product_router.get("/{product_id}")
async def product_get(product_id: uuid.UUID, service: ProductService = Depends()) -> typing.Union[None, ProductScheme]:
    return await service.get(id=product_id)


@product_router.put("/{product_id}", response_model=ProductScheme)
async def product_update(product_id: uuid.UUID, schema: ProductUpdateScheme, service: ProductService = Depends()):
    return await service.update(id=product_id, obj=schema)


@product_router.delete("/{product_id}")
async def product_delete(product_id: uuid.UUID, service: ProductService = Depends()):
    await service.delete(id=product_id)

@product_router.get("/barcode/{barcode}", response_model=ProductScheme)
async def product_by_barcode(barcode: str, service: ProductService = Depends()):
    return await service.product_by_barcode(barcode=barcode)
