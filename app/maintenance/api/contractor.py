from typing import List

from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import ContractorCreateScheme, ContractorScheme, ExceptionResponseSchema

contractor_router = APIRouter()

@contractor_router.post(
    "",
    response_model=List[ContractorScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_contractor_list(limit: int = Query(10, description="Limit")):
    return await ContractorScheme.get_all(limit=limit)

@contractor_router.post(
    "/create",
    response_model=ContractorScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_contractor(request: ContractorCreateScheme):
    entity = await request.create()
    return entity

@contractor_router.post(
    "/update",
    response_model=ContractorScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_contractor(request: ContractorCreateScheme):
    entity = await request.create()
    return entity

@contractor_router.post(
    "/delete",
    response_model=ContractorScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_contractor(request: ContractorCreateScheme):
    entity = await request.create()
    return entity
