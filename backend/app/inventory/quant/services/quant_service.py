import uuid
from typing import Any, Optional, List
from typing import TYPE_CHECKING

from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from starlette.requests import Request

from app.inventory.location import Location
from app.inventory.location.enums import BlockerEnum
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
    async def list(self, _filter: FilterSchemaType, size: int = 100):
        return await super(QuantService, self).list(_filter, size)

    @permit('quant_create')
    async def create(self, obj: CreateSchemaType, commit=True) -> ModelType:
        return await super(QuantService, self).create(obj, commit)

    @permit('quant_delete')
    async def delete(self, id: Any) -> None:
        return await super(QuantService, self).delete(id)

    async def get_available_quants(
            self,
            store_id: uuid.UUID,
            product_ids: [uuid.UUID] = None,
            id: uuid.UUID = None,
            exclude_id: uuid.UUID = None,
            location_classes: List[str] = None,
            location_ids: List[uuid.UUID] = None,
            package_ids: List[uuid.UUID] = None,
            location_type_ids: List[uuid.UUID] = None,
            lot_ids: List[uuid.UUID] = None,
            partner_id: uuid.UUID = None,
            quantity: float = 0
    ) -> List[Quant]:
        """
            Метод получения квантов по параметрам
        """
        query = (select(self.model)
                 .join(Location, self.model.location_id == Location.id)
                 .options(joinedload(self.model.location_rel))
                 .options(joinedload(self.model.package_rel))
                 )
        if id:
            query = query.where(self.model.id == id)
        else:
            if product_ids:
                query = query.where(self.model.product_id.in_(product_ids))
            if exclude_id:
                query = query.where(self.model.id != exclude_id)
            if store_id:
                query = query.where(self.model.store_id == store_id)
            if location_classes:
                query = query.where(Location.location_class.in_(location_classes))
            if location_ids:
                query = query.where(self.model.location_id.in_(location_ids))
            if package_ids:
                if None in package_ids:
                    query = query.where(or_(self.model.package_id.in_(package_ids), self.model.package_id.is_(None)))
                else:
                    query = query.where(self.model.package_id.in_(package_ids))
            if location_type_ids:
                query = query.where(Location.location_type_id.in_(location_type_ids))
            if lot_ids:
                if None in lot_ids:
                    query = query.where(or_(self.model.lot_id.in_(lot_ids), self.model.lot_id.is_(None)))
                else:
                    query = query.where(self.model.lot_id.in_(lot_ids))
            if quantity:
                query = query.where(self.model.quantity > quantity)

            """Если не указываем партнера, то партнер None тк тут не подходит логика --> Любой"""
            query = query.where(self.model.partner_id == partner_id)

        executed_data = await self.session.execute(query)
        return executed_data.scalars().all()
