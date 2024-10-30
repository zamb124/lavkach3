from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from app.inventory.location.models.location_models import LocationType
from app.inventory.location.schemas import LocationTypeCreateScheme, LocationTypeUpdateScheme, LocationTypeFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class LocationTypeService(BaseService[LocationType, LocationTypeCreateScheme, LocationTypeUpdateScheme, LocationTypeFilter]):
    def __init__(self, request:Request):
        super(LocationTypeService, self).__init__(request, LocationType,LocationTypeCreateScheme, LocationTypeUpdateScheme)

    @permit('location_type_update')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(LocationTypeService, self).update(id, obj)

    @permit('location_type_list')
    async def list(self, _filter: FilterSchemaType, size: int = None):
        return await super(LocationTypeService, self).list(_filter, size)

    @permit('location_type_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(LocationTypeService, self).create(obj)

    @permit('location_type_delete')
    async def delete(self, id: Any) -> None:
        return await super(LocationTypeService, self).delete(id)
