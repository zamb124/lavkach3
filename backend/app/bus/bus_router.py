from fastapi import APIRouter

from app.bus.bus.bus import ws_router

bus_router = APIRouter(prefix='/api/bus')
bus_router.include_router(ws_router, tags=["WS"])
