from fastapi import APIRouter

from app.bff.apps.inventory.order.order import order_router
from app.bff.apps.inventory.order_type.order_type import order_type_router

inventory_router = APIRouter()
inventory_router.include_router(order_router, prefix="/order", tags=["frontend"])
inventory_router.include_router(order_type_router, prefix="/order_type", tags=["frontend"])




