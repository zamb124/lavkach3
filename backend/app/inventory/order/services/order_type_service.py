from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.order.models.order_models import Order, OrderType
from app.inventory.order.schemas.order_type_schemas import OrderTypeCreateScheme, OrderTypeUpdateScheme, OrderTypeFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class OrderTypeService(BaseService[OrderType, OrderTypeCreateScheme, OrderTypeUpdateScheme, OrderTypeFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(OrderTypeService, self).__init__(request, OrderType, db_session)

    @permit('order_type_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(OrderTypeService, self).update(id, obj)

    @permit('order_type_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(OrderTypeService, self).list(_filter, size)

    @permit('order_type_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(OrderTypeService, self).create(obj)

    @permit('order_type_delete')
    async def delete(self, id: Any) -> None:
        return await super(OrderTypeService, self).delete(id)