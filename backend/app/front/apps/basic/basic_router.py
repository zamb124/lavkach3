from fastapi import APIRouter

from app.front.apps.basic.company.company import company_router
from app.front.apps.basic.product.product import product_router
from app.front.apps.basic.product.product_category import product_category_router
from app.front.apps.basic.product.product_storage_type import product_storage_type_router
from app.front.apps.basic.store.store import store_router
from app.front.apps.basic.uom.uom import uom_router
from app.front.apps.basic.uom.uom_category import uom_category_router
from app.front.apps.basic.user.user import user_router

basic_router = APIRouter()
basic_router.include_router(company_router, prefix="/company", tags=["company"])
basic_router.include_router(store_router, prefix="/store", tags=["store"])
basic_router.include_router(user_router, prefix="/user", tags=["user"])
basic_router.include_router(product_router, prefix="/product", tags=["product"])
basic_router.include_router(product_category_router, prefix="/product_category", tags=["product_category"])
basic_router.include_router(product_storage_type_router, prefix="/product_storage_type", tags=["product_storage_type"])
basic_router.include_router(uom_router, prefix="/uom", tags=["uom"])
basic_router.include_router(uom_category_router, prefix="/uom_category", tags=["uom_category"])




