from typing import List

from fastapi import APIRouter, Depends, Query
from app.company.schemas import (
    CompanyResponseSchema,
    ExceptionResponseSchema
)
from app.company.services import CompanyService

company_router = APIRouter()

@company_router.get(
    "",
    response_model=list[CompanyResponseSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_company_list(
    limit: int = Query(10, description="Limit")
):
    print('lol')
    a= await CompanyResponseSchema.get_all(limit=limit)
    return a
