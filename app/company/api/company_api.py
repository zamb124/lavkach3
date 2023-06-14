import uuid
import typing
from fastapi import APIRouter, Query
from app.company.schemas import (
    CompanyScheme,
    CompanyCreateScheme,
    CompanyUpdateScheme,
    ExceptionResponseSchema
)
from app.company.services.company_service import CompanyService

company_router = APIRouter()


@company_router.get(
    "",
    response_model=list[CompanyScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_company_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Prev LSN"),
):
    return await CompanyService().list(limit, cursor)


@company_router.post(
    "/create",
    response_model=CompanyScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_company(request: CompanyCreateScheme):
    return await CompanyService().create(obj=request)


@company_router.get(
    "/{company_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_company(company_id: uuid.UUID) -> typing.Union[None, CompanyScheme]:
    return await CompanyService().get(id=company_id)


@company_router.put(
    "/{company_id}",
    response_model=CompanyScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_company(company_id: uuid.UUID, request: CompanyUpdateScheme):
    return await CompanyService().update(id=company_id, obj=request)


@company_router.delete(
    "/{company_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_company(company_id: uuid.UUID):
    await CompanyService().delete(id=company_id)
