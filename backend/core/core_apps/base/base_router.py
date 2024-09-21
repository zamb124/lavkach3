from fastapi import APIRouter, Depends

from .auth.api.auth import auth_router
from .company.api.company_api import company_router
from .fundamental.base import fundamental_router
from .user.api.role_api import role_router
from .user.api.user_api import user_router
from ...fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

base_router = APIRouter(prefix='/api/base')
base_router.include_router(fundamental_router, prefix="", tags=["Base"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
base_router.include_router(user_router, prefix="/user", tags=["User"])
base_router.include_router(role_router, prefix="/role", tags=["Role"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
base_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
base_router.include_router(company_router, prefix="/company", tags=["Company"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])

