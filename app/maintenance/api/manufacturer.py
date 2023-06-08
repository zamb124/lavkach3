from typing import List, Union
import uuid
from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import ManufacturerCreateScheme, ExceptionResponseSchema, ManufacturerScheme, ManufacturerUpdateScheme

manufacturer_router = APIRouter()

@manufacturer_router.post(
    "",
    response_model=List[ManufacturerScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_manufacturer_list(limit: int = Query(10, description="Limit")):
    return await ManufacturerScheme.get_all(limit=limit)

@manufacturer_router.get(
    "/{supplier_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_manufacturer(company_id: uuid.UUID) -> Union[None, ManufacturerScheme]:
    return await ManufacturerScheme.get_by_id(id=company_id)
@manufacturer_router.post(
    "/create",
    response_model=ManufacturerScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_manufacturer(request: ManufacturerCreateScheme):
    entity = await request.create()
    return entity

@manufacturer_router.put(
    "/{supplier_id}",
    response_model=ManufacturerScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_manufacturer(contractor_id: uuid.UUID, request: ManufacturerUpdateScheme):
    entity = await request.update(id=contractor_id)
    return entity

@manufacturer_router.delete(
    "/{supplier_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_manufacturer(contractor_id: uuid.UUID):
    await ManufacturerScheme.delete_by_id(id=contractor_id)
