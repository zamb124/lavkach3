from collections import defaultdict
from typing import Any, Optional, List, Tuple, Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload, aliased
from starlette.requests import Request

from app.inventory.location import LocationType, Location
from app.inventory.order.enums.exceptions_order_type_enums import OrderTypeErrors
from app.inventory.order.enums.order_enum import OrderClass
from app.inventory.order.models.order_models import OrderType
from app.inventory.order.schemas.order_type_schemas import OrderTypeCreateScheme, OrderTypeUpdateScheme, OrderTypeFilter
from app.inventory.product_storage import ProductStorageType
from core.exceptions.module import ModuleException
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class OrderTypeService(BaseService[OrderType, OrderTypeCreateScheme, OrderTypeUpdateScheme, OrderTypeFilter]):
    def __init__(self, request: Request):
        super(OrderTypeService, self).__init__(request, OrderType, OrderTypeCreateScheme, OrderTypeUpdateScheme)

    @permit('order_type_update')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(OrderTypeService, self).update(id, obj)

    @permit('order_type_list')
    async def list(self, _filter: FilterSchemaType | dict, size: int = 100):
        return await super(OrderTypeService, self).list(_filter, size)

    @permit('order_type_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        obj.created_by = self.user.user_id
        obj.edited_by = self.user.user_id
        return await super(OrderTypeService, self).create(obj)

    @permit('order_type_delete')
    async def delete(self, id: Any) -> None:
        return await super(OrderTypeService, self).delete(id)

    async def get_appropriate_order_types(
            self, products: List[Tuple[UUID, UUID]],
            zone_dest_id: Optional[UUID] = None,
            location_dest_id: Optional[UUID] = None
    ) -> Dict[UUID, List[OrderType]]:
        """
        Метод подбирает подходящие order_type для каждого товара, основываясь на допустимых зонах и типах локаций.

        :param products: Список кортежей, где каждый кортеж содержит product_id и zone_src_id.
        :param zone_dest_id: Зона для дополнительной фильтрации order_type.
        :param location_dest_id: Идентификатор локации назначения для дополнительной фильтрации order_type.
        :return: Словарь, где ключом является product_id, а значением - список подходящих order_type в приоритетном
        порядке.
        """
        # Получаем все order_type
        location_model = self.env['location']
        order_types = await self.list({
            'order_class__in': [OrderClass.INTERNAL],
        })
        # Получаем все product_storage_type для указанных товаров
        product_ids = [product[0] for product in products]
        product_storage_types = await self.session.execute(
            select(ProductStorageType)
            .where(ProductStorageType.product_id.in_(product_ids))
            .options(joinedload(ProductStorageType.storage_type_rel))
        )
        product_storage_types = product_storage_types.scalars().all()

        # Создаем словарь для хранения допустимых зон и типов локаций для каждого товара
        product_storage_map = {
            pst.product_id: pst for pst in product_storage_types
        }

        # Создаем словарь для хранения подходящих order_type для каждого товара
        product_order_types = defaultdict(list)
        parents_location_src_map = await location_model.service.get_all_parent_zones(
            location_ids=[product[1] for product in products]
        )
        for product_id, zone_src_id in products:
            pst = product_storage_map.get(product_id)
            if not pst:
                raise ValueError(f'ProductStorageType for product_id={product_id} not found')

            # Получаем допустимые зоны и типы локаций для товара
            if location_dest_id:
                allowed_zones = await location_model.service.get_all_parent_zones(
                    location_ids=[location_dest_id]
                )[location_dest_id]
            elif zone_dest_id:
                allowed_zones = list(
                    set([zone_dest_id]) & set([UUID(i['zone_id']) for i in pst.storage_type_rel.allowed_zones])
                )
            else:
                allowed_zones = [UUID(i['zone_id']) for i in pst.storage_type_rel.allowed_zones]
            allowed_location_type_ids = pst.storage_type_rel.allowed_location_type_ids

            # Подбираем подходящие order_type для товара
            for order_type in order_types:
                zone_src_ids = parents_location_src_map.get(zone_src_id, [])
                if (any(zone_src_id in order_type.allowed_zone_src_ids for zone_src_id in zone_src_ids)
                        and any(zone in order_type.allowed_zone_dest_ids for zone in allowed_zones)
                        and any(loc_type_id in order_type.allowed_location_type_dest_ids
                                for loc_type_id in allowed_location_type_ids
                                )):
                    if order_type not in product_order_types[product_id]:
                        product_order_types[product_id].append(order_type)

            # Сортируем order_type по приоритету зон
            product_order_types[product_id].sort(
                key=lambda ot: next(
                    (zone['priority'] for zone in pst.storage_type_rel.allowed_zones
                     if zone['zone_id'] in ot.allowed_zone_dest_ids),
                    float('inf')
                )
            )

        return product_order_types

    async def get_appropriate_order_types_for_packages(
            self, packages: List[Tuple[UUID, UUID]],
            zone_dest_id: Optional[UUID] = None,
            location_dest_id: Optional[UUID] = None
    ) -> Dict[UUID, List[OrderType]]:
        """
        Метод подбирает подходящие order_type для каждого пакета, основываясь на допустимых зонах и типах локаций.

        :param packages: Список кортежей, где каждый кортеж содержит package_id и location_src_id.
        :param zone_dest_id: Зона для дополнительной фильтрации order_type.
        :param location_dest_id: Идентификатор локации назначения для дополнительной фильтрации order_type.
        :return: Словарь, где ключом является package_id, а значением - список подходящих order_type в приоритетном порядке.
        """
        # Получаем все order_type
        location_model = self.env['location']
        location_type_model = self.env['location_type']
        order_types = await self.list({
            'order_class__in': [OrderClass.INTERNAL],
        })

        # Создаем словарь для хранения подходящих order_type для каждого пакета
        package_order_types = defaultdict(list)
        parents_location_src_map = await location_model.service.get_all_parent_zones(
            location_ids=[package[1] for package in packages]
        )

        package_location_type_query = select(Location.location_type_id, Location.id).where(Location.id.in_([package[0] for package in packages]))
        package_location_type_result = await self.session.execute(package_location_type_query)
        package_location_type_ids = {row.id: row.location_type_id for row in package_location_type_result.fetchall()}

        # Преобразуем генератор в список
        package_location_type_ids_list = list(package_location_type_ids.values())

        # Получаем все Location, у которых location_type_id содержится в allowed_package_type_ids
        locations_query = (
            select(Location)
            .join(LocationType, Location.location_type_id == LocationType.id)
        ).where(
            LocationType.allowed_package_type_ids.contains(package_location_type_ids_list),
            Location.location_class == 'ZONE'
        ).options(joinedload(Location.location_type_rel))
        locations_result = await self.session.execute(locations_query)
        location_types_zones_dest_map = defaultdict(list)
        for location in locations_result.scalars().all():
            print(location.location_type_rel)
            if not location.location_type_rel:
                # не ебу, так надо
                location.location_type_rel = await location_type_model.service.get(location.location_type_id)
            for allowed_type_id in location.location_type_rel.allowed_package_type_ids:
                location_types_zones_dest_map[allowed_type_id].append(location.id)

        for package_id, location_src_id in packages:
            # Получаем допустимые зоны и типы локаций для пакета
            allowed_initial_zones = location_types_zones_dest_map.get(package_location_type_ids[package_id], {})
            if not allowed_initial_zones:
                raise ModuleException(
                    status_code=406, enum=OrderTypeErrors.SOURCE_LOCATION_ERROR,
                    message='No allowed zones found for the package',
                    args={'package_id': package_id}
                )
            if location_dest_id:
                allowed_zones = await location_model.service.get_all_parent_zones(
                    location_ids=[location_dest_id]
                )[location_dest_id]
            elif zone_dest_id:
                allowed_zones = [item for item in [zone_dest_id] if item in allowed_initial_zones]
            else:
                allowed_zones = allowed_initial_zones
            # Подбираем подходящие order_type для пакета
            for order_type in order_types:
                zone_src_ids = parents_location_src_map.get(location_src_id, [])
                if not zone_src_ids:
                    raise ModuleException(
                        status_code=406, enum=OrderTypeErrors.SOURCE_LOCATION_ERROR,
                        message='No allowed zones found for the package',
                        args={'package_id': package_id}
                    )
                if (any(zone_src_id in order_type.allowed_zone_src_ids for zone_src_id in zone_src_ids)
                        and any(zone in order_type.allowed_zone_dest_ids for zone in allowed_zones)):
                    if order_type not in package_order_types[package_id]:
                        package_order_types[package_id].append(order_type)
                else:
                    raise ModuleException(
                        status_code=406, enum=OrderTypeErrors.SOURCE_LOCATION_ERROR,
                        message='No allowed zones found for the package',
                        args={'package_id': package_id}
                    )
        return package_order_types
