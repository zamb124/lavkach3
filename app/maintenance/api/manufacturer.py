import uuid
import typing
from fastapi import APIRouter, Query
from app.maintenance.schemas import (
    ManufacturerScheme,
    ManufacturerCreateScheme,
    ManufacturerUpdateScheme,
    ExceptionResponseSchema
)
from app.maintenance.services.maintenance import ManufacturerService

manufacturer_router = APIRouter()


@manufacturer_router.get(
    "",
    response_model=list[ManufacturerScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def manufacturer_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Prev LSN"),
):
    return await ManufacturerService().list(limit, cursor)


@manufacturer_router.post(
    "/create",
    response_model=ManufacturerScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_manufacturer(request: ManufacturerCreateScheme):
    return await ManufacturerService().create(obj=request)


@manufacturer_router.get(
    "/{manufacturer_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_manufacturer(manufacturer_id: uuid.UUID) -> typing.Union[None, ManufacturerScheme]:
    return await ManufacturerService().get(id=manufacturer_id)


@manufacturer_router.put(
    "/{manufacturer_id}",
    response_model=ManufacturerScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_manufacturer(manufacturer_id: uuid.UUID, request: ManufacturerUpdateScheme):
    return await ManufacturerService().update(id=manufacturer_id, obj=request)


@manufacturer_router.delete(
    "/{manufacturer_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_manufacturer(manufacturer_id: uuid.UUID):
    await ManufacturerService().delete(id=manufacturer_id)
