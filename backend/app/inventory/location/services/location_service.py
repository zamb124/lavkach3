from typing import Any, Optional, List, Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload
from starlette.requests import Request

from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from app.inventory.location.models.location_models import Location, LocationClass

from app.inventory.location.enums import LocationClass
from app.inventory.location.models.location_models import Location
from app.inventory.location.schemas.location_schemas import LocationCreateScheme, LocationUpdateScheme, LocationFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class LocationService(BaseService[Location, LocationCreateScheme, LocationUpdateScheme, LocationFilter]):
    def __init__(self, request: Request):
        super(LocationService, self).__init__(request, Location, LocationCreateScheme, LocationUpdateScheme)

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

    async def get_location_hierarchy(
            self, location_ids: List[UUID],
            exclude_location_ids: List[UUID] = None,
            location_type_ids: List[UUID] = None,
            exclude_location_type_ids: List[UUID] = None,
            location_classes: List[str] = None,
            exclude_location_classes: List[str] = None,
    ) -> List[Location]:

        if exclude_location_ids:
            location_ids = list(set(location_ids) - set(exclude_location_ids))
        # Определяем CTE для рекурсивного запроса
        location_cte = (
            select(
                Location.id,
                Location.location_id,
                Location.location_class,
                Location.location_type_id,
            )
            .where(Location.id.in_(location_ids))
            .cte(name="location_cte", recursive=True)
        )

        # Определяем алиас для CTE
        location_alias = aliased(location_cte)

        # Добавляем рекурсивную часть запроса
        location_cte = location_cte.union_all(
            select(
                Location.id,
                Location.location_id,
                Location.location_class,
                Location.location_type_id,
            )
            .where(Location.location_id == location_alias.c.id)
            .where(Location.location_class.in_(location_classes) if location_classes else True)
            .where(Location.location_type_id.in_(location_type_ids) if location_type_ids else True)
            .where(Location.location_class.notin_(exclude_location_classes) if exclude_location_classes else True)
            .where(Location.location_type_id.notin_(exclude_location_type_ids) if exclude_location_type_ids else True)
        )

        # Выполняем запрос
        query = (
            select(Location)
            .options(joinedload(Location.location_type_rel))
            .where(Location.id.in_(select(location_cte.c.id)))
        )
        result = await self.session.execute(query)
        locations = result.scalars().all()

        return locations

    async def get_all_parent_zones(self, location_ids: List[UUID]) -> Dict[UUID, List[Optional[Location]]]:
        LocationAlias = aliased(Location)

        # Создаем рекурсивный CTE-запрос для поиска всех родителей для каждого location_id
        cte = (
            select(Location.id, Location.location_id, Location.location_class)
            .where(Location.id.in_(location_ids))
            .cte(name="cte", recursive=True)
        )

        cte = cte.union_all(
            select(Location.id, Location.location_id, Location.location_class)
            .join(cte, Location.id == cte.c.location_id)
        )

        # Запрос для получения всех родителей с location_class == ZONE для каждого location_id
        query = (
            select(cte.c.id, cte.c.location_id, cte.c.location_class)
            .where(cte.c.location_class == LocationClass.ZONE)
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        # Формируем словарь, где ключом является location_id, а значением - список всех родительских зон
        parent_zones = {location_id: [] for location_id in location_ids}
        for row in rows:
            if row.location_id:
                parent_zones[row.id].append(row.location_id)

        # Добавляем сами зоны, если они не имеют родителей
        for location_id in location_ids:
            if not parent_zones[location_id]:
                location = await self.session.execute(
                    select(Location).where(Location.id == location_id)
                )
                location = location.scalar_one_or_none()
                if location and location.location_class == LocationClass.ZONE:
                    parent_zones[location_id].append(location_id)

        return parent_zones