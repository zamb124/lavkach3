from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, computed_field
from pydantic.types import UUID4

from app.inventory.location.enums import LocationClass
from app.inventory.quant.models import Quant
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel, BasicField as Field
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class QuantBaseScheme(BasicModel):
    vars: Optional[dict] = None
    product_id: UUID4 = Field(title='Product ID', model='product')
    store_id: UUID4 = Field(title='Store ID', model='store')
    location_id: Optional[UUID4] = Field(
        title='Location ID', model='location',
        filter={'location_class__not_in': LocationClass.PACKAGE.value},
    )
    package_id: Optional[UUID4] = Field(
        title='Package ID', model='location',
        filter={'location_class__in': LocationClass.PACKAGE.value},
    )
    lot_id: Optional[UUID4] = Field(default=None, title='Lot ID', model='lot')
    partner_id: Optional[UUID4] = Field(default=None, title='Partner ID', model='partner')
    quantity: float = Field(title='Quantity')
    reserved_quantity: Optional[float] = Field(default=0.0, title='Reserved Quantity')
    incoming_quantity: Optional[float] = Field(default=0.0, title='Incoming Quantity')
    expiration_datetime: Optional[datetime] = Field(default=None, title='Expiration Datetime')
    uom_id: UUID4 = Field(title='UOM ID', model='uom')
    move_ids: Optional[list[UUID4]] = Field(default=[], title='Move IDs')

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Quant
        service = 'app.inventory.quant.services.QuantService'

class QuantUpdateScheme(QuantBaseScheme):
    store_id: Optional[UUID4] = Field(default=None, title='Store ID', model='store')
    quantity: Optional[float] = Field(default=None, title='Quantity')
    reserved_quantity: Optional[float] = Field(default=None, title='Reserved Quantity')
    uom_id: Optional[UUID4] = Field(default=None, title='UOM ID', model='uom')


class QuantCreateScheme(QuantBaseScheme):
    ...


class QuantScheme(QuantCreateScheme, TimeStampScheme):
    company_id: UUID4 = Field(title='Company ID', model='company')
    lsn: int
    id: UUID4

    @computed_field
    @property
    def title(self) -> str:
        return f'Q-{self.quantity} | R-{self.reserved_quantity} | I-{self.incoming_quantity}'


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
