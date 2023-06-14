import uuid
import typing
from fastapi import APIRouter, Query
from app.maintenance.schemas import (
    ContractorScheme,
    ContractorCreateScheme,
    ContractorUpdateScheme,
    ExceptionResponseSchema
)
from app.maintenance.services.maintenance_service import ContractorService

contractor_router = APIRouter()


@contractor_router.get(
    "",
    response_model=list[ContractorScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def contractor_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Prev LSN"),
):
    return await ContractorService().list(limit, cursor)


@contractor_router.post(
    "/create",
    response_model=ContractorScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_contractor(request: ContractorCreateScheme):
    return await ContractorService().create(obj=request)


@contractor_router.get(
    "/{contractor_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_contractor(contractor_id: uuid.UUID) -> typing.Union[None, ContractorScheme]:
    return await ContractorService().get(id=contractor_id)


@contractor_router.put(
    "/{contractor_id}",
    response_model=ContractorScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_contractor(contractor_id: uuid.UUID, request: ContractorUpdateScheme):
    return await ContractorService().update(id=contractor_id, obj=request)


@contractor_router.delete(
    "/{contractor_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_contractor(contractor_id: uuid.UUID):
    await ContractorService().delete(id=contractor_id)
