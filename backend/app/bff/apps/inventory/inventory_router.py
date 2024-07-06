from fastapi import APIRouter

from app.bff.apps.inventory.move import move_router
from app.bff.apps.inventory.order.order import order_router
from app.bff.apps.inventory.order_type.order_type import order_type_router
from app.bff.apps.inventory.inventory import inventory

inventory_router = APIRouter()
inventory_router.include_router(inventory)
inventory_router.include_router(order_router, prefix="/order")
inventory_router.include_router(order_router, prefix="/order", tags=["order"])
inventory_router.include_router(order_type_router, prefix="/order_type", tags=["order_type"])
inventory_router.include_router(move_router, prefix="/move", tags=["move"])
