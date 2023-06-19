import uuid
import typing
from backend.app.company.schemas import (
    CompanyScheme,
    CompanyCreateScheme,
    CompanyUpdateScheme,
    ExceptionResponseSchema
)
from backend.app.company.services.company_service import CompanyService
from backend.core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from fastapi import APIRouter, Depends, Query

company_router = APIRouter(
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@company_router.get("",response_model=list[CompanyScheme])
async def get_company_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Cursor"),
):
    return await CompanyService().list(limit, cursor)


@company_router.post("/create",response_model=CompanyScheme)
async def create_company(request: CompanyCreateScheme):
    return await CompanyService().create(obj=request)


@company_router.get("/{company_id}")
async def load_company(company_id: uuid.UUID) -> typing.Union[None, CompanyScheme]:
    return await CompanyService().get(id=company_id)


@company_router.put("/{company_id}",response_model=CompanyScheme)
async def update_company(company_id: uuid.UUID, request: CompanyUpdateScheme):
    return await CompanyService().update(id=company_id, obj=request)


@company_router.delete("/{company_id}")
async def delete_company(company_id: uuid.UUID):
    await CompanyService().delete(id=company_id)
