import datetime
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.order.models.order_models import Suggest
from app.inventory.order.schemas.suggest_schemas import SuggestCreateScheme, SuggestUpdateScheme, SuggestFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType



class SuggestService(BaseService[Suggest, SuggestCreateScheme, SuggestUpdateScheme, SuggestFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(SuggestService, self).__init__(request, Suggest, SuggestCreateScheme, SuggestUpdateScheme, db_session)

    @permit('suggest_edit')
    async def update(self, id: Any, obj: UpdateSchemaType, commit=False) -> Optional[ModelType]:
        return await super(SuggestService, self).update(id, obj, commit=commit)

    @permit('suggest_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(SuggestService, self).list(_filter, size)

    @permit('suggest_create')
    async def create(self, obj: CreateSchemaType, commit=False) -> ModelType:
        return await super(SuggestService, self).create(obj, commit)

    @permit('suggest_delete')
    async def delete(self, id: Any) -> None:
        return await super(SuggestService, self).delete(id)

    @permit('order_view')
    async def suggest_confirm(self, id: Any) -> Optional[ModelType]:
        suggest = await self.get(id)
        suggest.status = 'confirmed'
        suggest.confirm_datetime = datetime.datetime.now()
        return suggest
