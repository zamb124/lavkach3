from fastapi import APIRouter, Depends
from app.bff.apps.basic.company.company import company_router
from app.bff.apps.inventory.order import order_router
from core.fastapi.dependencies.bff_auth import Token


inventory_router = APIRouter()
inventory_router.include_router(order_router, prefix="/order", tags=["frontend"])




