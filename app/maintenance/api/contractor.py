from typing import List

from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import ContractorCreateScheme, ContractorScheme, ExceptionResponseSchema

contractor_router = APIRouter()

@contractor_router.post(
    "",
    response_model=ContractorScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_contractor(request: ContractorCreateScheme):
    entity = await request.create()
    return entity
