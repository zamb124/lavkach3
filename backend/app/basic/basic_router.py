from fastapi import APIRouter, Depends

from app.basic.partner.api.partner_api import partner_router
from app.basic.product.api import product_category_router, product_router
from app.basic.store.api.store_api import store_router
from app.basic.uom.api.uom_api import uom_router, uom_category_router
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

basic_router = APIRouter(prefix='/api/basic')
basic_router.include_router(partner_router, prefix="/partner", tags=["Partner"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(store_router, prefix="/store", tags=["Store"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(uom_category_router, prefix="/uom_category", tags=["Uom", "Category"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(uom_router, prefix="/uom", tags=["Uom", "Uom"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(product_category_router, prefix="/product_category", tags=["ProductCategory"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
basic_router.include_router(product_router, prefix="/product", tags=["Product"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])

