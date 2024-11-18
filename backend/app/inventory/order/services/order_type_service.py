from typing import Any, Optional

from sqlalchemy import select
from starlette.requests import Request

from app.inventory.order.models.order_models import OrderType
from app.inventory.order.schemas.order_type_schemas import OrderTypeCreateScheme, OrderTypeUpdateScheme, OrderTypeFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class OrderTypeService(BaseService[OrderType, OrderTypeCreateScheme, OrderTypeUpdateScheme, OrderTypeFilter]):
    def __init__(self, request:Request):
        super(OrderTypeService, self).__init__(request, OrderType,OrderTypeCreateScheme, OrderTypeUpdateScheme)

    @permit('order_type_update')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(OrderTypeService, self).update(id, obj)

    @permit('order_type_list')
    async def list(self, _filter: FilterSchemaType, size: int=100):
        return await super(OrderTypeService, self).list(_filter, size)

    @permit('order_type_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        obj.created_by = self.user.user_id
        obj.edited_by = self.user.user_id
        return await super(OrderTypeService, self).create(obj)

    @permit('order_type_delete')
    async def delete(self, id: Any) -> None:
        return await super(OrderTypeService, self).delete(id)

    async def get_by_attrs(self, **kwargs):
        """
            Метод получения объекта по атрибутам
        """
        query = select(self.model)
        if id:
            query = query.where(self.model.id == id)
        else:
            if product_id:
                query = query.where(self.model.product_id == product_id)
            if exclude_id:
                query = query.where(self.model.id != exclude_id)
            if store_id:
                query = query.where(self.model.store_id == store_id)
            if location_class_ids:
                query = query.where(self.model.location_class.in_(location_class_ids))
            if location_ids:
                query = query.where(self.model.location_id.in_(location_ids))
            if location_type_ids:
                query = query.where(self.model.location_type_id.in_(location_type_ids))
            if lot_ids:
                query = query.where(self.model.lot_id.in_(lot_ids))

            """Если не указываем партнера, то партнер None тк тут не подходит логика --> Любой"""
            query = query.where(self.model.partner_id == partner_id)

        executed_data = await self.session.execute(query)
        return executed_data.scalars().all()