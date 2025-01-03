from fastapi import APIRouter, Depends

from app.foodhub.foodhub.api.prescription_api import prescription_router as ps_router
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

router = APIRouter(prefix='/api/foodhub')
router.include_router(ps_router, prefix="/foodhub", tags=["Foodhub"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])

