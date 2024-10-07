from fastapi import APIRouter, Depends

from app.prescription.prescription.api.prescription_api import prescription_router as ps_router
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

router = APIRouter(prefix='/api/prescription')
router.include_router(ps_router, prefix="/prescription", tags=["Prescription"], dependencies=[Depends(PermissionDependency([IsAuthenticated]))])

