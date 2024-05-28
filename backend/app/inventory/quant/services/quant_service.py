import uuid
from typing import Any, Optional
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.location.models import Location
from app.inventory.quant.models.quants_models import Quant
from app.inventory.quant.schemas.quants_schemas import QuantCreateScheme, QuantUpdateScheme, QuantFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType

if TYPE_CHECKING:
    from app.inventory.order.models import OrderType


class QuantService(BaseService[Quant, QuantCreateScheme, QuantUpdateScheme, QuantFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(QuantService, self).__init__(request, Quant, QuantCreateScheme, QuantUpdateScheme, db_session)

    @permit('quant_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(QuantService, self).update(id, obj)

    @permit('quant_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(QuantService, self).list(_filter, size)

    @permit('quant_create')
    async def create(self, obj: CreateSchemaType, commit=False) -> ModelType:
        return await super(QuantService, self).create(obj, commit)

    @permit('quant_delete')
    async def delete(self, id: Any) -> None:
        return await super(QuantService, self).delete(id)

    async def get_available_quants(
            self,
            product_id:                         uuid.UUID,
            store_id:                           uuid.UUID,
            id:                                 uuid.UUID = None,
            location_class_ids:                 [uuid.UUID] = None,
            location_ids:                       [uuid.UUID] = None,
            location_type_ids:                  [uuid.UUID] = None,
            lot_ids:                            [uuid.UUID] = None,
            partner_id:                         uuid.UUID = None,
    ) -> list(Quant):
        """
            Метод получения квантов по параметрам
        """
        query = select(self.model)
        if id:
            query = query.where(self.model.id == id)
        else:
            if product_id:
                query = query.where(self.model.product_id == product_id)
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
