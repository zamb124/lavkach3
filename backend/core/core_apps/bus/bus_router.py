from fastapi import APIRouter

from .bus.api.bus_api import bus_router as router
from .bus.api.bus_ws_api import ws_router

bus_router = APIRouter(prefix='/api/bus')
bus_router.include_router(router, prefix='/bus')
bus_router.include_router(ws_router, prefix='/ws')
