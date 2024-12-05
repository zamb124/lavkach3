from fastapi import APIRouter

from app.front.apps.inventory.app import inventory_app
from app.front.apps.inventory.inventory import inventory
from app.front.apps.inventory.location import location_router
from app.front.apps.inventory.move import move_router
from app.front.apps.inventory.move_log import move_log_router
from app.front.apps.inventory.order.order import order_router
from app.front.apps.inventory.order_type.order_type import order_type_router
from app.front.apps.inventory.stock_reports import stocks_reports_router
from app.front.apps.inventory.store import store_router
from app.front.apps.inventory.store_monitor.store_monitor import store_monitor_router
from app.front.apps.inventory.store_staff import store_staff_router
from app.front.apps.inventory.suggest import suggest_router
from app.front.apps.inventory.product_storage_type import product_storage_type_router
from app.front.apps.inventory.storage_type import storage_type_router

inventory_router = APIRouter()
inventory_router.include_router(inventory)
inventory_router.include_router(store_monitor_router, prefix="/store_monitor")
inventory_router.include_router(inventory_app, prefix="/app")
inventory_router.include_router(order_router, prefix="/order", tags=["order"])
inventory_router.include_router(order_type_router, prefix="/order_type", tags=["order"])
inventory_router.include_router(location_router, prefix="/location", tags=["location"])
inventory_router.include_router(move_router, prefix="/move", tags=["move"])
inventory_router.include_router(stocks_reports_router, prefix="/stock_reports", tags=["stocks_reports"])
inventory_router.include_router(move_log_router, prefix="/move_log", tags=["move_log"])
inventory_router.include_router(suggest_router, prefix="/suggest", tags=["suggest"])
inventory_router.include_router(product_storage_type_router, prefix="/product_storage_type", tags=["product_storage_type"])
inventory_router.include_router(storage_type_router, prefix="/storage_type", tags=["storage_type"])

inventory_router.include_router(store_router, prefix="/store", tags=["store"])
inventory_router.include_router(store_staff_router, prefix="/store_staff", tags=["store_staff"])
