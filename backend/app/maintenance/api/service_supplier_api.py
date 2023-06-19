import typing
import uuid

from fastapi import APIRouter, Depends, Query

from backend.app.maintenance.schemas import (
    ServiceSupplierScheme,
    ServiceSupplierCreateScheme,
    ServiceSupplierUpdateScheme,
    ExceptionResponseSchema
)
from backend.app.maintenance.services.maintenance_service import ServiceSupplierService
from backend.core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

supplier_router = APIRouter(
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@supplier_router.get("", response_model=list[ServiceSupplierScheme])
async def supplier_list(limit: int = Query(10, description="Limit"), cursor: int = Query(0, description="Prev LSN"), ):
    return await ServiceSupplierService().list(limit, cursor)


@supplier_router.post("/create", response_model=ServiceSupplierScheme)
async def create_supplier(request: ServiceSupplierCreateScheme):
    return await ServiceSupplierService().create(obj=request)


@supplier_router.get("/{supplier_id}")
async def load_supplier(supplier_id: uuid.UUID) -> typing.Union[None, ServiceSupplierScheme]:
    return await ServiceSupplierService().get(id=supplier_id)


@supplier_router.put("/{supplier_id}", response_model=ServiceSupplierScheme)
async def update_supplier(supplier_id: uuid.UUID, request: ServiceSupplierUpdateScheme):
    return await ServiceSupplierService().update(id=supplier_id, obj=request)


@supplier_router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: uuid.UUID):
    await ServiceSupplierService().delete(id=supplier_id)
