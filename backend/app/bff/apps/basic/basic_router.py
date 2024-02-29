from fastapi import APIRouter
from app.bff.apps.basic.company.company import company_router


basic_router = APIRouter()
basic_router.include_router(company_router, prefix="/company", tags=["frontend"])




