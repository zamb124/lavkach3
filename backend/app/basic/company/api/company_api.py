import uuid
import typing

from starlette.requests import Request

from app.basic.company.schemas import (
    CompanyScheme,
    CompanyCreateScheme,
    CompanyUpdateScheme,
    ExceptionResponseSchema,
    CompanyListSchema
)
from app.basic.company.services.company_service import CompanyService
from fastapi import APIRouter, Query, Depends

from core.fastapi.dependencies import PermissionDependency, IsAuthenticated

company_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@company_router.get("",
                    response_model=CompanyListSchema,
                    )
async def get_company_list(
        request: Request,
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Cursor"),
):
    return await CompanyService(request).list(limit, cursor)


@company_router.post("/create", response_model=CompanyScheme)
async def create_company(request: Request, schema: CompanyCreateScheme):
    return await CompanyService(request).create(obj=schema)


@company_router.get("/{company_id}")
async def load_company(request: Request, company_id: uuid.UUID):
    return await CompanyService(request).get(id=company_id)


@company_router.put("/{company_id}", response_model=CompanyScheme)
async def update_company(request: Request, company_id: uuid.UUID, schema: CompanyUpdateScheme):
    return await CompanyService(request).update(id=company_id, obj=schema)


@company_router.delete("/{company_id}")
async def delete_company(request: Request, company_id: uuid.UUID):
    await CompanyService(request).delete(id=company_id)
