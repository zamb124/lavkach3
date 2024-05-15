from fastapi import APIRouter

from core.fastapi.frontend.base import router

base_router = APIRouter()
base_router.include_router(router, prefix="/base", tags=["base"])




