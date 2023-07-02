import uuid

from fastapi import APIRouter, Query
from fastapi_filter import FilterDepends
from starlette.requests import Request

from app.basic.uom.schemas import (
    UomCategoryScheme,
    UomCategoryCreateScheme,
    UomCategoryUpdateScheme,
    UomCategoryListSchema,
    UomCategoryFilter
)
from app.basic.uom.schemas import (
    UomScheme,
    UomCreateScheme,
    UomUpdateScheme,
    ExceptionResponseSchema,
    UomListSchema,
    UomFilter
)
from app.basic.uom.services.uom_service import UomCategoryService, UomService

uom_category_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)
uom_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@uom_category_router.get("", response_model=UomCategoryListSchema)
async def uom_category_list(
        request: Request,
        model_filter: UomCategoryFilter = FilterDepends(UomCategoryFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await UomCategoryService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@uom_category_router.post("/create", response_model=UomCategoryScheme)
async def uom_category_create(request: Request, schema: UomCategoryCreateScheme):
    return await UomCategoryService(request).create(obj=schema)


@uom_category_router.get("/{category_id}")
async def uom_category_get(request: Request, category_id: uuid.UUID):
    return await UomCategoryService(request).get(id=category_id)


@uom_category_router.put("/{category_id}", response_model=UomCategoryScheme)
async def uom_category_update(request: Request, category_id: uuid.UUID, schema: UomCategoryUpdateScheme):
    return await UomCategoryService(request).update(id=category_id, obj=schema)


@uom_category_router.delete("/{category_id}")
async def uom_category_delete(request: Request, category_id: uuid.UUID):
    await UomCategoryService(request).delete(id=category_id)


#####################################UOM########################################
@uom_router.get("", response_model=UomListSchema)
async def uom_list(
        request: Request,
        model_filter: UomFilter = FilterDepends(UomFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await UomService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@uom_router.post("/create", response_model=UomScheme)
async def uom_create(request: Request, schema: UomCreateScheme):
    return await UomService(request).create(obj=schema)


@uom_router.get("/{uom_id}")
async def uom_get(request: Request, uom_id: uuid.UUID):
    return await UomService(request).get(id=uom_id)


@uom_router.put("/{uom_id}", response_model=UomScheme)
async def uom_update(request: Request, uom_id: uuid.UUID, schema: UomUpdateScheme):
    return await UomService(request).update(id=uom_id, obj=schema)


@uom_router.delete("/{uom_id}")
async def uom_delete(request: Request, uom_id: uuid.UUID):
    await UomService(request).delete(id=uom_id)
