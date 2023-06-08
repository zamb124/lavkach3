from typing import List, Union
import uuid
from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import ContractorCreateScheme, ContractorScheme, ExceptionResponseSchema, ContractorUpdateScheme

contractor_router = APIRouter()

@contractor_router.get(
    "",
    response_model=List[ContractorScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_contractor_list(limit: int = Query(10, description="Limit")):
    return await ContractorScheme.get_all(limit=limit)

@contractor_router.get(
    "/{contractor_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_contractor(company_id: uuid.UUID) -> Union[None, ContractorScheme]:
    return await ContractorScheme.get_by_id(id=company_id)
@contractor_router.post(
    "/create",
    response_model=ContractorScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_contractor(request: ContractorCreateScheme):
    entity = await request.create()
    return entity

@contractor_router.put(
    "/{contractor_id}",
    response_model=ContractorScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_contractor(contractor_id: uuid.UUID, request: ContractorUpdateScheme):
    entity = await request.update(id=contractor_id)
    return entity

@contractor_router.delete(
    "/{contractor_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_contractor(contractor_id: uuid.UUID):
    await ContractorScheme.delete_by_id(id=contractor_id)
