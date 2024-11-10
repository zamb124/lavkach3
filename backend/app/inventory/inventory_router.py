from sys import prefix

from fastapi import APIRouter, Depends

from app.inventory.inventory_api import inventory_router
from app.inventory.location.api import location_router, location_type_router
from app.inventory.order.api import order_router, order_type_router
from app.inventory.order.api.move_api import move_router
from app.inventory.order.api.move_log_api import move_log_router
from app.inventory.order.api.suggest_api import suggest_router
from app.inventory.product_storage.api import product_storage_type_router
from app.inventory.product_storage.api.storage_type_api import storage_type_router
from app.inventory.quant.api import quant_router, lot_router
from app.inventory.store_staff.api import store_staff_router
from core.fastapi.dependencies import PermissionDependency, IsAuthenticated

router = APIRouter(
    prefix="/api/inventory",
)
router.include_router(
    inventory_router,
    tags=["Inventory"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    quant_router,
    prefix="/quant",
    tags=["Quant"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    lot_router,
    prefix="/lot",
    tags=["Lot"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    location_type_router,
    prefix="/location_type",
    tags=["LocationType"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    location_router,
    prefix="/location",
    tags=["Location"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    order_router,
    prefix="/order",
    tags=["Order"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    move_router,
    prefix="/move",
    tags=["Order"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    move_log_router,
    prefix="/move_log",
    tags=["MoveLog"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    suggest_router,
    prefix="/suggest",
    tags=["Order"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    order_type_router,
    prefix="/order_type",
    tags=["OrderType"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    storage_type_router,
    prefix="/storage_type",
    tags=["StorageType"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    product_storage_type_router,
    prefix="/product_storage_type",
    tags=["ProductStorageType"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
router.include_router(
    store_staff_router,
    prefix="/store_staff",
    tags=["StoreStaff"],
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
