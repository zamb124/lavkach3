from fastapi import APIRouter, Depends

from app.inventory.quant.api import quant_router, lot_router
from app.inventory.order.api import order_router, order_type_router
from app.inventory.location.api import location_router, location_type_router
from core.fastapi.dependencies import PermissionDependency, IsAuthenticated

inventory_router = APIRouter()
inventory_router.include_router(quant_router, prefix="/api/inventory/quant", tags=["Quant"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
inventory_router.include_router(lot_router, prefix="/api/inventory/lot", tags=["Lot"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
inventory_router.include_router(location_type_router, prefix="/api/inventory/location_type", tags=["LocationType"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
inventory_router.include_router(location_router, prefix="/api/inventory/location", tags=["Location"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
inventory_router.include_router(order_router, prefix="/api/inventory/order", tags=["Order"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
inventory_router.include_router(order_type_router, prefix="/api/inventory/order_type", tags=["OrderType"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
