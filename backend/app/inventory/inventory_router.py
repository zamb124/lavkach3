from fastapi import APIRouter, Depends

from app.inventory.quant.api.quants_api import quant_router
from app.inventory.location.api.location_api import location_router

inventory_router = APIRouter()
inventory_router.include_router(quant_router, prefix="/api/inventory/quants", tags=["Inventory"])
inventory_router.include_router(location_router, prefix="/api/inventory/quants", tags=["Inventory"])

