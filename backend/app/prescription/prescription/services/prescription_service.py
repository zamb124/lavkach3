from typing import Any, Optional

from starlette.requests import Request

from app.prescription.prescription.models.prescription_models import Prescription
from app.prescription.prescription.schemas.prescription_schemas import PrescriptionCreateScheme, \
    PrescriptionUpdateScheme, PrescriptionFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class PrescriptionService(BaseService[Prescription, PrescriptionCreateScheme, PrescriptionUpdateScheme, PrescriptionFilter]):
    def __init__(self, request:Request):
        super(PrescriptionService, self).__init__(request, Prescription,PrescriptionCreateScheme, PrescriptionUpdateScheme)

    @permit('prescription_update')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(PrescriptionService, self).update(id, obj)

    @permit('prescription_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(PrescriptionService, self).list(_filter, size)

    @permit('prescription_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(PrescriptionService, self).create(obj)

    @permit('prescription_delete')
    async def delete(self, id: Any) -> None:
        return await super(PrescriptionService, self).delete(id)


