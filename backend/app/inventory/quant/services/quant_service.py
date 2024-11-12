import uuid
from typing import Any, Optional
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from starlette.requests import Request

from app.inventory.location import Location
from app.inventory.quant.models.quants_models import Quant
from app.inventory.quant.schemas.quants_schemas import QuantCreateScheme, QuantUpdateScheme, QuantFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType

if TYPE_CHECKING:
    pass


class QuantService(BaseService[Quant, QuantCreateScheme, QuantUpdateScheme, QuantFilter]):
    def __init__(self, request: Request):
        super(QuantService, self).__init__(request, Quant, QuantCreateScheme, QuantUpdateScheme)

    @permit('quant_update')
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
            store_id: uuid.UUID,
            product_id: uuid.UUID = None,
            id: uuid.UUID = None,
            exclude_id: uuid.UUID = None,
            location_classes: list[str] = None,
            location_ids: list[uuid.UUID] = None,
            location_type_ids: list[uuid.UUID] = None,
            lot_ids: list[uuid.UUID] = None,
            partner_id: uuid.UUID = None,
            quantity: float = 0
    ) -> list[Quant]:
        """
            Метод получения квантов по параметрам
        """
        query = select(self.model).join(Location, self.model.location_id == Location.id)
        if id:
            query = query.where(self.model.id == id)
        else:
            if product_id:
                query = query.where(self.model.product_id == product_id)
            if exclude_id:
                query = query.where(self.model.id != exclude_id)
            if store_id:
                query = query.where(self.model.store_id == store_id)
            if location_classes:
                query = query.where(Location.location_class.in_(location_classes))
            if location_ids:
                query = query.where(self.model.location_id.in_(location_ids))
            if location_type_ids:
                query = query.where(Location.location_type_id.in_(location_type_ids))
            if lot_ids:
                query = query.where(self.model.lot_id.in_(lot_ids))
            if quantity:
                query = query.where(self.model.quantity > quantity)

            """Если не указываем партнера, то партнер None тк тут не подходит логика --> Любой"""
            query = query.where(self.model.partner_id == partner_id)

        executed_data = await self.session.execute(query)
        return executed_data.scalars().all()
