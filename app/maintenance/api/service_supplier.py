from typing import List, Union
import uuid
from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import ServiceSupplierCreateScheme, ExceptionResponseSchema, ServiceSupplierScheme, ServiceSupplierUpdateScheme

supplier_router = APIRouter()

@supplier_router.post(
    "",
    response_model=List[ServiceSupplierScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_contractor_list(limit: int = Query(10, description="Limit")):
    return await ServiceSupplierScheme.get_all(limit=limit)

@supplier_router.get(
    "/{supplier_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_contractor(company_id: uuid.UUID) -> Union[None, ServiceSupplierScheme]:
    return await ServiceSupplierScheme.get_by_id(id=company_id)
@supplier_router.post(
    "/create",
    response_model=ServiceSupplierScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_contractor(request: ServiceSupplierCreateScheme):
    entity = await request.create()
    return entity

@supplier_router.put(
    "/{supplier_id}",
    response_model=ServiceSupplierScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_contractor(contractor_id: uuid.UUID, request: ServiceSupplierUpdateScheme):
    entity = await request.update(id=contractor_id)
    return entity

@supplier_router.delete(
    "/{supplier_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_contractor(contractor_id: uuid.UUID):
    await ServiceSupplierScheme.delete_by_id(id=contractor_id)
