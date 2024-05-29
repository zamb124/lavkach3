from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, computed_field
from pydantic.types import UUID4

from app.inventory.location.enums import LocationClass
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.quant.models import Quant


class QuantBaseScheme(BaseModel):
    vars: Optional[dict] = None
    product_id: UUID4
    store_id: UUID4
    location_class: LocationClass
    location_type_id: UUID4
    location_id: Optional[UUID4] = None
    lot_id: Optional[UUID4] = None
    partner_id: Optional[UUID4] = None
    quantity: float
    reserved_quantity: Optional[float]
    incoming_quantity: Optional[float]
    expiration_datetime: Optional[datetime] = None
    uom_id: UUID4
    move_ids: Optional[list[UUID4]] = None

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Quant
        service = 'app.inventory.quant.services.QuantService'

class QuantUpdateScheme(QuantBaseScheme):
    store_id: Optional[UUID4] = None
    quantity: Optional[float] = None
    reserved_quantity: Optional[float] = None
    uom_id: Optional[UUID4] = None


class QuantCreateScheme(QuantBaseScheme):
    ...


class QuantScheme(QuantCreateScheme, TimeStampScheme):
    company_id: UUID4
    lsn: int
    id: UUID4

    @computed_field
    @property
    def title(self) -> str:
        return f'{self.quantity} | {self.reserved_quantity} | {self.incoming_quantity}'

    class Config:
        from_attributes = True


class QuantFilter(BaseFilter):
    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Quant
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["company_id", "product_id", "lot_id"]


class QuantListSchema(GenericListSchema):
    data: Optional[List[QuantScheme]]
