from fastapi import APIRouter

from app.bff.apps.basic.basic_router import basic_router
from app.bff.apps.inventory import inventory_router
from app.bff.bff import index_router
from app.terminal.basic.terminal_router import terminal_router # bad?


bff_router = APIRouter()
bff_router.include_router(index_router, prefix="", tags=["frontend"])
bff_router.include_router(basic_router, prefix="/basic", tags=["frontend"])
bff_router.include_router(inventory_router, prefix="/inventory", tags=["frontend"])
bff_router.include_router(terminal_router, prefix="/terminal", tags=["frontend"])




