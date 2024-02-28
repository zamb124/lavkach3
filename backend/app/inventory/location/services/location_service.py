from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.quant.models.quants_models import Quant
from app.inventory.quant.schemas.quants_schemas import QuantCreateScheme, QuantUpdateScheme, QuantFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class QuantService(BaseService[Quant, QuantCreateScheme, QuantUpdateScheme, QuantFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(QuantService, self).__init__(request, Quant, db_session)

    @permit('quant_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(QuantService, self).update(id, obj)

    @permit('quant_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(QuantService, self).list(_filter, size)

    @permit('quant_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(QuantService, self).create(obj)

    @permit('quant_delete')
    async def delete(self, id: Any) -> None:
        return await super(QuantService, self).delete(id)
