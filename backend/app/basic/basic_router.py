from fastapi import APIRouter, Depends

from app.basic.fundamental.base import fundamental_router
from app.basic.user.api.user_api import user_router
from app.basic.user.api.role_api import role_router
from app.basic.uom.api.uom_api import uom_router, uom_category_router
from app.basic.partner.api.partner_api import partner_router
from app.basic.auth.api.auth import auth_router
from app.basic.company.api.company_api import company_router
from app.basic.store.api.store_api import store_router
from app.basic.product.api import product_category_router, product_storage_type_router, product_router
from app.basic.bus.bus import ws_router
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

basic_router = APIRouter(prefix='/api/basic')
basic_router.include_router(fundamental_router, prefix="", tags=["Base"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(user_router, prefix="/user", tags=["User"])
basic_router.include_router(role_router, prefix="/role", tags=["Role"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(partner_router, prefix="/partner", tags=["Partner"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
basic_router.include_router(company_router, prefix="/company", tags=["Company"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(store_router, prefix="/store", tags=["Store"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(uom_category_router, prefix="/uom_category", tags=["Uom", "Category"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(uom_router, prefix="/uom", tags=["Uom", "Uom"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(product_category_router, prefix="/product_category", tags=["ProductCategory"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(product_storage_type_router, prefix="/product_storage_type", tags=["ProductStorageType"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(product_router, prefix="/product", tags=["Product"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(ws_router,  tags=["WS"])

