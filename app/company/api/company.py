import uuid
import typing

from fastapi import APIRouter, Depends, Query
from app.company.schemas import (
    CompanySchema,
    ExceptionResponseSchema
)

company_router = APIRouter()

@company_router.post(
    "",
    response_model=list[CompanySchema],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_company_list(limit: int = Query(10, description="Limit")):
    a = await CompanySchema.get_all(limit=limit)
    return a

@company_router.post(
    "",
    response_model=CompanySchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_company(request: CompanySchema):
    entity = await request.create()
    return entity


@company_router.get(
    "/{company_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_store(company_id: uuid.UUID) -> typing.Union[None, CompanySchema]:
    return await CompanySchema.get_by_id(id=company_id)
