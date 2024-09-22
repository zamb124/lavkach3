from typing import Any, Optional


from starlette.requests import Request
from ...bus.models.bus_models import Bus
from ...bus.shemas.bus_schemas import BusCreateScheme, BusUpdateScheme, BusFilter
from .....permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class BusService(BaseService[Bus, BusCreateScheme, BusUpdateScheme, BusFilter]):
    def __init__(self, request: Request):
        super(BusService, self).__init__(request, Bus,BusCreateScheme, BusUpdateScheme)

    @permit('bus_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(BusService, self).update(id, obj)

    @permit('bus_list')
    async def list(self, _filter: FilterSchemaType, size: int = 100):
        return await super(BusService, self).list(_filter, size)

    @permit('bus_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        from ...bus_tasks import send_message
        bus_entity = await super(BusService, self).create(obj)
        send_message = await send_message.kiq({
            'bus_id': bus_entity.id,
            'cache_tag': bus_entity.cache_tag,
            'message': bus_entity.message,
            'company_id': bus_entity.company_id,
            'vars': bus_entity.vars,
        })
        return bus_entity

    @permit('bus_delete')
    async def delete(self, id: Any) -> None:
        return await super(BusService, self).delete(id)
