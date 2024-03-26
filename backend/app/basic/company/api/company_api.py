import uuid

from fastapi import APIRouter, Query
from fastapi_filter import FilterDepends
from starlette.requests import Request

from app.basic.company.schemas import (
    CompanyScheme,
    CompanyCreateScheme,
    CompanyUpdateScheme,
    ExceptionResponseSchema,
    CompanyListSchema,
    CompanyFilter
)
from app.basic.company.services.company_service import CompanyService
from app.basic.user.schemas import LoginResponseSchema

company_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@company_router.get("", response_model=CompanyListSchema)
async def company_list(
        request: Request,
        model_filter: CompanyFilter = FilterDepends(CompanyFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await CompanyService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@company_router.post("", response_model=CompanyScheme)
async def company_create(request: Request, schema: CompanyCreateScheme):
    return await CompanyService(request).create(obj=schema)


@company_router.get("/{company_id}", response_model=CompanyScheme)
async def company_get(request: Request, company_id: uuid.UUID):
    return await CompanyService(request).get(id=company_id)


@company_router.put("/{company_id}", response_model=CompanyScheme)
async def company_update(request: Request, company_id: uuid.UUID, schema: CompanyUpdateScheme):
    return await CompanyService(request).update(id=company_id, obj=schema)


@company_router.delete("/{company_id}")
async def company_delete(request: Request, company_id: uuid.UUID):
    return await CompanyService(request).delete(id=company_id)



