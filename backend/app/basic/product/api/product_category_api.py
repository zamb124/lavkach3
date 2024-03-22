import typing
import uuid

from fastapi import APIRouter, Query, Request
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
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@product_category_router.get("", response_model=ProductCategoryListSchema)
async def product_category_list(
        request: Request,
        model_filter: ProductCategoryFilter = FilterDepends(ProductCategoryFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await ProductCategoryService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@product_category_router.post("", response_model=ProductCategoryScheme)
async def product_category_create(request: Request, schema: ProductCategoryCreateScheme):
    return await ProductCategoryService(request).create(obj=schema)


@product_category_router.get("/{product_category_id}")
async def product_category_get(request: Request, product_category_id: uuid.UUID) -> typing.Union[None, ProductCategoryScheme]:
    return await ProductCategoryService(request).get(id=product_category_id)


@product_category_router.put("/{product_category_id}", response_model=ProductCategoryScheme)
async def product_category_update(request: Request, product_category_id: uuid.UUID,schema: ProductCategoryUpdateScheme):
    return await ProductCategoryService(request).update(id=product_category_id, obj=schema)


@product_category_router.delete("/{product_category_id}")
async def product_category_delete(request: Request, product_category_id: uuid.UUID):
    await ProductCategoryService(request).delete(id=product_category_id)
