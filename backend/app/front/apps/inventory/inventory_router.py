from fastapi import APIRouter

from app.front.apps.inventory.app import inventory_app
from app.front.apps.inventory.move import move_router
from app.front.apps.inventory.order.order import order_router
from app.front.apps.inventory.order_type.order_type import order_type_router
from app.front.apps.inventory.inventory import inventory

inventory_router = APIRouter()
inventory_router.include_router(inventory)
inventory_router.include_router(inventory_app, prefix="/app")
inventory_router.include_router(order_router, prefix="/order")
inventory_router.include_router(order_router, prefix="/order", tags=["order"])
inventory_router.include_router(order_type_router, prefix="/order_type", tags=["order_type"])
inventory_router.include_router(move_router, prefix="/move", tags=["move"])
