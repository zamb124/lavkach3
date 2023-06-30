from fastapi import APIRouter, Depends

from .maintenance.api.manufacturer_api import manufacturer_router
from .maintenance.api.asset_log_api import asset_log_router
from .maintenance.api.asset_type_api import asset_type_router
from .maintenance.api.asset_api import asset_router
from .maintenance.api.model_api import model_router
from .maintenance.api.order_api import order_router


router = APIRouter()
router.include_router(manufacturer_router, prefix="/api/manufacturer", tags=["Manufacturer"])
router.include_router(model_router, prefix="/api/model", tags=["Model"])
router.include_router(asset_type_router, prefix="/api/assets_type", tags=["AssetType"])
router.include_router(asset_router, prefix="/api/asset", tags=["Asset"])
router.include_router(asset_log_router, prefix="/api/asset_log", tags=["AssetLog"])
router.include_router(order_router, prefix="/api/order", tags=["Order"])



__all__ = ["router"]
