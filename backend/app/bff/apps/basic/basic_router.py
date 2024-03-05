from fastapi import APIRouter, Depends
from app.bff.apps.basic.company.company import company_router
from core.fastapi.dependencies.bff_auth import Token


basic_router = APIRouter()
basic_router.include_router(company_router, prefix="/company", tags=["frontend"])




