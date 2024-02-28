from fastapi import APIRouter, Depends

from app.inventory.quant.api.quants_api import quant_router
from app.basic.store.api.store_api import store_router
from core.fastapi.middlewares.company import company_depends
from app.basic.bus.bus import ws_router
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

inventory_router = APIRouter()
inventory_router.include_router(quant_router, prefix="/api/inventory/quants", tags=["Inventory"])

