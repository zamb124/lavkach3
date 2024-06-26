from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.bus.bus.models.bus_models import Bus
from app.bus.bus.shemas.bus_schemas import BusCreateScheme, BusUpdateScheme, BusFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class BusService(BaseService[Bus, BusCreateScheme, BusUpdateScheme, BusFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(BusService, self).__init__(request, Bus,BusCreateScheme, BusUpdateScheme,db_session)

    @permit('bus_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(BusService, self).update(id, obj)

    @permit('bus_list')
    async def list(self, _filter: FilterSchemaType, size: int = 100):
        return await super(BusService, self).list(_filter, size)

    @permit('bus_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(BusService, self).create(obj)

    @permit('bus_delete')
    async def delete(self, id: Any) -> None:
        return await super(BusService, self).delete(id)
