from fastapi import APIRouter, Depends
from app.bff.bff import index_router


bff_router = APIRouter()
bff_router.include_router(index_router, prefix="", tags=["frontend"])




