from fastapi import APIRouter

from app.front.apps.basic.basic_router import basic_router
from app.front.apps.inventory import inventory_router
from app.front.front import index_router
from core.frontend.router import base_router


front_router = APIRouter()
front_router.include_router(base_router)
front_router.include_router(index_router, prefix="", tags=["frontend"])
front_router.include_router(basic_router, prefix="/basic", tags=["basic"])
front_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])


