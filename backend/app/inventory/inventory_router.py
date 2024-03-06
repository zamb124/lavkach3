from fastapi import APIRouter, Depends

from app.inventory.quant.api.quants_api import quant_router
from app.inventory.order.api.order_api import order_router
from app.inventory.order.api.order_type_api import order_type_router
from app.inventory.location.api.location_api import location_router
from core.fastapi.dependencies import PermissionDependency, IsAuthenticated

inventory_router = APIRouter()
inventory_router.include_router(quant_router, prefix="/api/inventory/quants", tags=["Inventory"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
inventory_router.include_router(location_router, prefix="/api/inventory/location", tags=["Inventory"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
inventory_router.include_router(order_router, prefix="/api/inventory/order", tags=["Inventory"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
inventory_router.include_router(order_type_router, prefix="/api/inventory/order_type", tags=["Inventory"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
