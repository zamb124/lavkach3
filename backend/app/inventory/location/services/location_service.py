from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.location.models.location_models import Location
from app.inventory.location.schemas.location_schemas import LocationCreateScheme, LocationUpdateScheme, LocationFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class LocationService(BaseService[Location, LocationCreateScheme, LocationUpdateScheme, LocationFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(LocationService, self).__init__(request, Location,LocationCreateScheme, LocationUpdateScheme, db_session)

    @permit('location_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(LocationService, self).update(id, obj)

    @permit('location_list')
    async def list(self, _filter: FilterSchemaType, size: int = None):
        return await super(LocationService, self).list(_filter, size)

    @permit('location_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(LocationService, self).create(obj)

    @permit('location_delete')
    async def delete(self, id: Any) -> None:
        return await super(LocationService, self).delete(id)
