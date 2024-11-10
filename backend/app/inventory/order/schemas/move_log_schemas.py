from __future__ import annotations

from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic.types import UUID4

from app.inventory.location.enums import LocationClass
from app.inventory.order.enums.order_enum import MoveLogType
from app.inventory.order.models import MoveLog
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicField as Field
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class MoveLogBaseScheme(BasicModel):
    type: MoveLogType = Field(title='Move Type', table=True, readonly=True, description='Type of move')
    order_id: Optional[UUID4] = Field(default=None, title='Order ID', model='order')
    move_id: UUID4 = Field(title='Move ID', model='move', readonly=True)
    product_id: UUID4 = Field( title='Product', table=True, model='product')
    store_id: UUID4 = Field(title='Store', table=True, form=True, model='store')
    location_class: LocationClass = Field(title='Location Class')
    location_id: UUID4 = Field(title='Location', model='location', table=True)
    lot_id: Optional[UUID4] = Field(default=None, title='Lot', table=True, model='lot')
    partner_id: Optional[UUID4] = Field(default=None, title='Partner ID', model='partner')
    quantity: float = Field(title='Quantity', table=True)
    reserved_quantity: float = Field(title='Reserced Qty', table=True)
    incoming_quantity: float = Field(title='Incoming Qty', table=True)
    created_by: UUID4 = Field(title='Created By',  model='user')
    edited_by: UUID4 = Field(title='Edit By', model='user')

    class Config:
        orm_model = MoveLog

class MoveLogUpdateScheme(MoveLogBaseScheme):
    ...


class MoveLogCreateScheme(MoveLogBaseScheme):
    ...


class MoveLogScheme(MoveLogCreateScheme, TimeStampScheme):
    company_id: UUID4 = Field(model='company', title='Company')
    lsn: int
    id: UUID4



class MoveLogFilter(BaseFilter):
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store', model='store')
    order_id__in: Optional[List[UUID4]] = Field(default=None, title='Order', model='order')
    move_id__in: Optional[List[UUID4]] = Field(default=None, title='Move', model='move')
    product_id__in: Optional[List[UUID4]] = Field(default=None, title='Product', model='product')
    location_id__in: Optional[List[UUID4]] = Field(default=None, title='Location', model='location')
    lot_id__in: Optional[List[UUID4]] = Field(default=None, title='Lot', model='lot')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = MoveLog
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["order_id", "product_id"]


class MoveLogListSchema(GenericListSchema):
    data: Optional[List[MoveLogScheme]]
