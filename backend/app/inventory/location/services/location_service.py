from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from starlette.requests import Request

from app.inventory.location.enums import LocationClass
from app.inventory.location.models.location_models import Location
from app.inventory.location.schemas.location_schemas import LocationCreateScheme, LocationUpdateScheme, LocationFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class LocationService(BaseService[Location, LocationCreateScheme, LocationUpdateScheme, LocationFilter]):
    def __init__(self, request:Request):
        super(LocationService, self).__init__(request, Location,LocationCreateScheme, LocationUpdateScheme)

    @permit('location_update')
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


    async def get_location_hierarchy(self, allowed_location_src_ids: list):
        # Определяем CTE для рекурсивного запроса
        location_cte = (
            select(
                Location.id,
                Location.location_id,
                Location.title,
                Location.location_class,
                Location.location_type_id,
                Location.store_id
            )
            .where(Location.id.in_(allowed_location_src_ids))
            .where(Location.location_class != LocationClass.PACKAGE)
            .cte(name="location_cte", recursive=True)
        )

        # Определяем алиас для CTE
        location_alias = aliased(location_cte)

        # Добавляем рекурсивную часть запроса
        location_cte = location_cte.union_all(
            select(
                Location.id,
                Location.location_id,
                Location.title,
                Location.location_class,
                Location.location_type_id,
                Location.store_id
            )
            .where(Location.location_id == location_alias.c.id)
            .where(Location.location_class != LocationClass.PACKAGE)
        )

        # Выполняем запрос
        query = select(location_cte)
        result = await self.session.execute(query)
        locations = result.scalars().all()

        return locations