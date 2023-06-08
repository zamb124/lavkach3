from typing import List, Union
import uuid
from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import ManufacturerCreateScheme, ExceptionResponseSchema, ManufacturerScheme, ManufacturerUpdateScheme

manufacturer_router = APIRouter()

@manufacturer_router.get(
    "",
    response_model=List[ManufacturerScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_manufacturer_list(limit: int = Query(10, description="Limit")):
    return await ManufacturerScheme.get_all(limit=limit)

@manufacturer_router.get(
    "/{manufacturer_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_manufacturer(manufacturer_id: uuid.UUID) -> Union[None, ManufacturerScheme]:
    return await ManufacturerScheme.get_by_id(id=manufacturer_id)
@manufacturer_router.post(
    "/create",
    response_model=ManufacturerScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_manufacturer(request: ManufacturerCreateScheme):
    entity = await request.create()
    return entity

@manufacturer_router.put(
    "/{manufacturer_id}",
    response_model=ManufacturerScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_manufacturer(manufacturer_id: uuid.UUID, request: ManufacturerUpdateScheme):
    entity = await request.update(id=manufacturer_id)
    return entity

@manufacturer_router.delete(
    "/{manufacturer_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_manufacturer(manufacturer_id: uuid.UUID):
    await ManufacturerScheme.delete_by_id(id=manufacturer_id)
