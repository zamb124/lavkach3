import typing
import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from app.basic.product.schemas import (
    ProductCategoryScheme,
    ProductCategoryCreateScheme,
    ProductCategoryUpdateScheme,
    ProductCategoryListSchema,
    ProductCategoryFilter,
    ExceptionResponseSchema,
)
from app.basic.product.services import ProductCategoryService

product_category_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@product_category_router.get("", response_model=ProductCategoryListSchema)
async def product_category_list(
        model_filter: ProductCategoryFilter = FilterDepends(ProductCategoryFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: ProductCategoryService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@product_category_router.post("", response_model=ProductCategoryScheme)
async def product_category_create(schema: ProductCategoryCreateScheme, service: ProductCategoryService = Depends()):
    return await service.create(obj=schema)


@product_category_router.get("/{product_category_id}")
async def product_category_get(product_category_id: uuid.UUID, service: ProductCategoryService = Depends()) -> typing.Union[None, ProductCategoryScheme]:
    return await service.get(id=product_category_id)


@product_category_router.put("/{product_category_id}", response_model=ProductCategoryScheme)
async def product_category_update(product_category_id: uuid.UUID, schema: ProductCategoryUpdateScheme, service: ProductCategoryService = Depends()):
    return await service.update(id=product_category_id, obj=schema)


@product_category_router.delete("/{product_category_id}")
async def product_category_delete(product_category_id: uuid.UUID, service: ProductCategoryService = Depends()):
    await service.delete(id=product_category_id)
