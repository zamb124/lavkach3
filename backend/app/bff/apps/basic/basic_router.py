from fastapi import APIRouter

from app.bff.apps.basic.company.company import company_router
from app.bff.apps.basic.product.product import product_router
from app.bff.apps.basic.product.product_category import product_category_router
from app.bff.apps.basic.product.product_storage_type import product_storage_type_router
from app.bff.apps.basic.store.store import store_router
from app.bff.apps.basic.uom.uom import uom_router
from app.bff.apps.basic.uom.uom_category import uom_category_router
from app.bff.apps.basic.user.user import user_router

basic_router = APIRouter()
basic_router.include_router(company_router, prefix="/company", tags=["frontend"])
basic_router.include_router(store_router, prefix="/store", tags=["frontend"])
basic_router.include_router(user_router, prefix="/user", tags=["frontend"])
basic_router.include_router(product_router, prefix="/product", tags=["frontend"])
basic_router.include_router(product_category_router, prefix="/product_category", tags=["frontend"])
basic_router.include_router(product_storage_type_router, prefix="/product_storage_type", tags=["frontend"])
basic_router.include_router(uom_router, prefix="/uom", tags=["frontend"])
basic_router.include_router(uom_category_router, prefix="/uom_category", tags=["frontend"])




