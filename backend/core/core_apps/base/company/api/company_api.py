import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends

from ....base.company.schemas import (
    CompanyScheme,
    CompanyCreateScheme,
    CompanyUpdateScheme,
    ExceptionResponseSchema,
    CompanyListSchema,
    CompanyFilter
)
from ....base.company.services.company_service import CompanyService

company_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@company_router.get("", response_model=CompanyListSchema)
async def company_list(
        model_filter: CompanyFilter = FilterDepends(CompanyFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: CompanyService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@company_router.post("", response_model=CompanyScheme)
async def company_create(schema: CompanyCreateScheme, service: CompanyService = Depends()):
    return await service.create(obj=schema)


@company_router.get("/{company_id}", response_model=CompanyScheme)
async def company_get(company_id: uuid.UUID, service: CompanyService = Depends()):
    return await service.get(id=company_id)


@company_router.put("/{company_id}", response_model=CompanyScheme)
async def company_update(company_id: uuid.UUID, schema: CompanyUpdateScheme, service: CompanyService = Depends()):
    return await service.update(id=company_id, obj=schema)


@company_router.delete("/{company_id}")
async def company_delete(company_id: uuid.UUID, service: CompanyService = Depends()):
    return await service.delete(id=company_id)



