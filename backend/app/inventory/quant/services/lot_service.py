from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.quant.models.quants_models import Lot
from app.inventory.quant.schemas import LotCreateScheme, LotUpdateScheme, LotFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class LotService(BaseService[Lot, LotCreateScheme, LotUpdateScheme, LotFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(LotService, self).__init__(request, Lot, db_session)

    @permit('lot_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(LotService, self).update(id, obj)

    @permit('lot_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(LotService, self).list(_filter, size)

    @permit('lot_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(LotService, self).create(obj)

    @permit('lot_delete')
    async def delete(self, id: Any) -> None:
        return await super(LotService, self).delete(id)
