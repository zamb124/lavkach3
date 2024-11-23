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

    async def get_all_parent_zones(self, location_ids: List[UUID]) -> Dict[UUID, List[Optional[UUID]]]:
        """
        Метод отдает словарь с ключом location_id, который был на входе в виде списка, и значением -
        все родительские зоны по каждому location_id.
        При этом, если location_id сам является зоной, то в результате будет также сам location_id.

        :param location_ids: Список идентификаторов локаций (UUID), для которых нужно найти родительские зоны.
        :return: Dict[UUID, List[UUID] Словарь, где ключом является location_id, а значением - список всех родительских
        зон для данного location_id.
        """
        # Сначала получаем location_id для каждого id из location_ids
        initial_query = select(
            Location.id, Location.location_id, Location.location_class).where(Location.id.in_(location_ids))
        initial_result = await self.session.execute(initial_query)
        initial_rows = initial_result.fetchall()

        parent_zones = {
            row.id: [row.id] if row.location_class == LocationClass.ZONE else []
            for row in initial_rows
        }
        # Обновляем location_ids на основе полученных location_id
        location_ids = {row.id: row.location_id for row in initial_rows}
        # Создаем рекурсивный CTE-запрос для поиска всех родителей для каждого location_id
        cte = (
            select(Location.id, Location.location_id, Location.location_class)
            .where(Location.id.in_(location_ids.values()))
            .cte(name="cte", recursive=True)
        )

        cte = cte.union_all(
            select(Location.id, Location.location_id, Location.location_class)
            .join(cte, Location.id == cte.c.location_id)
        )

        # Запрос для получения всех родителей с location_class == ZONE для каждого location_id
        query = (
            select(cte.c.id, cte.c.location_id)
            .where(cte.c.location_class == LocationClass.ZONE)
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        # Формируем словарь, где ключом является location_id, а значением - список всех родительских зон
        rows_dict = {row.id: row.location_id for row in rows}

        for _id, location_id in location_ids.items():
            current_id = location_id
            while current_id in rows_dict:
                parent_id = rows_dict[current_id]
                if parent_id:
                    parent_zones[_id].append(current_id)
                    current_id = parent_id
                else:
                    parent_zones[_id].append(current_id)
                    break

        return parent_zones
