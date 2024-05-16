from fastapi import APIRouter
from app.terminal.suggest.api.orders import orders_router

terminal_router = APIRouter()
terminal_router.include_router(orders_router, prefix="", tags=["frontend"])

