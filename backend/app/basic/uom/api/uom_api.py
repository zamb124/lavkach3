import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from app.basic.uom.schemas import (
    UomCategoryScheme,
    UomCategoryCreateScheme,
    UomCategoryUpdateScheme,
    UomCategoryListSchema,
    UomCategoryFilter, ConvertSchema
)
from app.basic.uom.schemas import (
    UomScheme,
    UomCreateScheme,
    UomUpdateScheme,
    ExceptionResponseSchema,
    UomListSchema,
    UomFilter
)
from app.basic.uom.services.uom_category_service import UomCategoryService
from app.basic.uom.services.uom_service import UomService

uom_category_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)
uom_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@uom_category_router.get("", response_model=UomCategoryListSchema)
async def uom_category_list(
        model_filter: UomCategoryFilter = FilterDepends(UomCategoryFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: UomCategoryService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@uom_category_router.post("", response_model=UomCategoryScheme)
async def uom_category_create(schema: UomCategoryCreateScheme, service: UomCategoryService = Depends()):
    return await service.create(obj=schema)


@uom_category_router.get("/{category_id}")
async def uom_category_get(category_id: uuid.UUID, service: UomCategoryService = Depends()):
    return await service.get(id=category_id)


@uom_category_router.put("/{category_id}", response_model=UomCategoryScheme)
async def uom_category_update(category_id: uuid.UUID, schema: UomCategoryUpdateScheme, service: UomCategoryService = Depends()):
    return await service.update(id=category_id, obj=schema)


@uom_category_router.delete("/{category_id}")
async def uom_category_delete(category_id: uuid.UUID, service: UomCategoryService = Depends()):
    await service.delete(id=category_id)


#####################################UOM########################################
@uom_router.get("", response_model=UomListSchema)
async def uom_list(
        model_filter: UomFilter = FilterDepends(UomFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: UomService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@uom_router.post("", response_model=UomScheme)
async def uom_create(schema: UomCreateScheme, service: UomService = Depends()):
    return await service.create(obj=schema)


@uom_router.get("/{uom_id}")
async def uom_get(uom_id: uuid.UUID, service: UomService = Depends()):
    return await service.get(id=uom_id)


@uom_router.put("/{uom_id}", response_model=UomScheme)
async def uom_update(uom_id: uuid.UUID, schema: UomUpdateScheme, service: UomService = Depends()):
    return await service.update(id=uom_id, obj=schema)


@uom_router.delete("/{uom_id}")
async def uom_delete(uom_id: uuid.UUID, service: UomService = Depends()):
    await service.delete(id=uom_id)


@uom_router.post("/convert", response_model=list[ConvertSchema])
async def uom_convert(schema: list[ConvertSchema], service: UomService = Depends()):
    await service.convert(schema)
