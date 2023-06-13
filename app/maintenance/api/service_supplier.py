import uuid
import typing
from fastapi import APIRouter, Query
from app.maintenance.schemas import (
    ServiceSupplierScheme,
    ServiceSupplierCreateScheme,
    ServiceSupplierUpdateScheme,
    ExceptionResponseSchema
)
from app.maintenance.services.maintenance import ServiceSupplierService

supplier_router = APIRouter()


@supplier_router.get(
    "",
    response_model=list[ServiceSupplierScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def supplier_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Prev LSN"),
):
    return await ServiceSupplierService().list(limit, cursor)


@supplier_router.post(
    "/create",
    response_model=ServiceSupplierScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_supplier(request: ServiceSupplierCreateScheme):
    return await ServiceSupplierService().create(obj=request)


@supplier_router.get(
    "/{supplier_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_supplier(supplier_id: uuid.UUID) -> typing.Union[None, ServiceSupplierScheme]:
    return await ServiceSupplierService().get(id=supplier_id)


@supplier_router.put(
    "/{supplier_id}",
    response_model=ServiceSupplierScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_supplier(supplier_id: uuid.UUID, request: ServiceSupplierUpdateScheme):
    return await ServiceSupplierService().update(id=supplier_id, obj=request)


@supplier_router.delete(
    "/{supplier_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_supplier(supplier_id: uuid.UUID):
    await ServiceSupplierService().delete(id=supplier_id)
