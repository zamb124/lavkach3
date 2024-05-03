import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.location.enums import LocationClass, VirtualLocationClass
from app.inventory.location.models import LocationType, Location

from app.inventory.quant.models.quants_models import Quant, Lot
from app.inventory.quant.schemas.quants_schemas import QuantCreateScheme, QuantUpdateScheme, QuantFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType
from typing import TYPE_CHECKING
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
            order_type: 'OrderType',
            product_id: uuid.uuid4 = None,
            package: Location = None,
            partner_id: uuid.uuid4 = None
    ) -> list(Quant):
        assert any([product_id, package])
        filter = {}
        query = select(self.model)

        if partner_id:
            query = query.where(self.model.partner_id == partner_id)
        if order_type.allowed_location_class_src_ids:
            query = query.where(self.model.location_class.in_(order_type.allowed_location_class_src_ids))
        if order_type.allowed_location_type_src_ids:
            query = query.where(self.model.location_type.in_(order_type.allowed_location_type_src_ids))
        if order_type.store_id:
            query = query.where(self.model.store_id == order_type.store_id)
        if product_id:
            filter.update({})
            query = query.where(self.model.product_id == product_id)
        # if location:
        #     query = query.where(self.model.location_id == location.id)
        # if lot:
        #     query = query.where(self.model.lot_id == lot.id)

        executed_data = await self.session.execute(query)
        return executed_data.scalars().all()

