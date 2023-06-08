from fastapi import APIRouter

from .user.api.user import user_router
from .auth.api.auth import auth_router
from .company.api.company import company_router
from .store.api.store import store_router
from .maintenance.api.contractor import contractor_router
from .maintenance.api.service_supplier import supplier_router
from .maintenance.api.manufacturer import manufacturer_router

router = APIRouter()
router.include_router(user_router, prefix="/api/users", tags=["User"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(company_router, prefix="/api/company", tags=["Company"])
router.include_router(store_router, prefix="/api/store", tags=["Store"])
router.include_router(contractor_router, prefix="/api/contractor", tags=["Contractor"])
router.include_router(supplier_router, prefix="/api/supplier", tags=["Supplier"])
router.include_router(manufacturer_router, prefix="/api/manufacturer", tags=["Manufacturer"])


__all__ = ["router"]
