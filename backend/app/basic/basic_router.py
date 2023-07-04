from fastapi import APIRouter, Depends
from app.routers import router

from app.basic.fundamental.base import fundamental_router
from app.basic.user.api.user_api import user_router
from app.basic.user.api.role_api import role_router
from app.basic.uom.api.uom_api import uom_router, uom_category_router
from app.basic.partner.api.partner_api import partner_router
from app.basic.auth.api.auth import auth_router
from app.basic.company.api.company_api import company_router
from app.basic.store.api.store_api import store_router
from core.fastapi.middlewares.company import company_depends
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

basic_router = APIRouter()
router.include_router(fundamental_router, prefix="/api/fundamental", tags=["Base"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
router.include_router(user_router, prefix="/api/user", tags=["User"])
router.include_router(role_router, prefix="/api/role", tags=["Role"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
router.include_router(partner_router, prefix="/api/partner", tags=["Partner"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(company_router, prefix="/api/company", tags=["Company"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
router.include_router(store_router, prefix="/api/store", tags=["Store"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
router.include_router(uom_category_router, prefix="/api/uom/category", tags=["Uom", "Category"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
router.include_router(uom_router, prefix="/api/uom/uom", tags=["Uom", "Uom"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])

