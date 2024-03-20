from fastapi import APIRouter, Depends
from app.bff.apps.basic.company.company import company_router
from app.bff.apps.basic.store.store import store_router
from core.fastapi.dependencies.bff_auth import Token


basic_router = APIRouter()
basic_router.include_router(company_router, prefix="/company", tags=["frontend"])
basic_router.include_router(store_router, prefix="/store", tags=["frontend"])




