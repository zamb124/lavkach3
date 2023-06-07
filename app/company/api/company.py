from typing import List

from fastapi import APIRouter, Depends, Query
from app.company.schemas import (
    CompanySchema,
    ExceptionResponseSchema
)

company_router = APIRouter()

@company_router.get(
    "",
    response_model=list[CompanySchema],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_company_list(limit: int = Query(10, description="Limit")):
    print('lol')
    a= await CompanySchema.get_all(limit=limit)
    return a

@company_router.post(
    "",
    response_model=CompanySchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_company(request: CompanySchema):
    res = await request.create()
    return await request.get_by_id(res)
