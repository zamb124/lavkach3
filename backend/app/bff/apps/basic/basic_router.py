from fastapi import APIRouter

from app.bff.apps.basic.company.company import company_router
from app.bff.apps.basic.store.store import store_router
from app.bff.apps.basic.user.user import user_router

basic_router = APIRouter()
basic_router.include_router(company_router, prefix="/company", tags=["frontend"])
basic_router.include_router(store_router, prefix="/store", tags=["frontend"])
basic_router.include_router(user_router, prefix="/user", tags=["frontend"])




