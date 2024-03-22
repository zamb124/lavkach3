from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Any
from datetime import date

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, field_validator, model_validator, model_serializer
from pydantic.types import UUID4

from app.inventory.location.enums import PutawayStrategy
from core.schemas import BaseFilter

from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.order.models import Order
from app.inventory.order.models.order_models import OrderStatus
from app.inventory.order.schemas.order_type_schemas import OrderTypeScheme

class OrderBaseScheme(BaseModel):
    vars: Optional[dict] = None
    parent_id: Optional[UUID4] = None
    external_number: Optional[str] = None
    store_id: UUID4
    partner_id: Optional[UUID4] = None
    lot_id: Optional[UUID4] = None
    order_type_id: Optional[UUID4] = None
    origin_number: Optional[str] = None
    planned_date: Optional[datetime]
    actual_date: Optional[datetime]
    created_by: UUID4
    edited_by: UUID4
    expiration_datetime: Optional[datetime]
    users_ids: Optional[list[UUID4]] = []
    description: Optional[str]
    status: OrderStatus


class OrderUpdateScheme(OrderBaseScheme):
    vars: Optional[dict] = None
    external_number: Optional[str] = None
    lot_id: Optional[UUID4] = None
    origin_type: Optional[str] = None
    origin_number: Optional[str] = None
    planned_date: Optional[datetime] = None
    expiration_datetime: Optional[datetime] = None
    description: Optional[str] = None
    partner_id: Optional[UUID4] = None
    order_type_id: UUID4 = None

class OrderCreateScheme(OrderBaseScheme):
    company_id: UUID4

    class Config:
        extra = 'allow'

class OrderScheme(OrderCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company_id: UUID4
    moves_list_rel: Optional[list[UUID4]] = []
    number: str
    order_type: 'OrderTypeScheme'

    class Config:
        orm_mode = True


def empty_erray(val):
    if val:
        return val

class OrderFilter(BaseFilter):
    planned_date__gte: Optional[datetime] = Field(alias='planned_date_from', description="bigger or equal planned date", default=None)
    planned_date__lt: Optional[datetime] = Field(alias='planned_date_to', description="less planned date", default=None)
    status__in: Optional[List[OrderStatus]] = Field(alias="status", default=None)
    date_planned_range: Optional[str] = Field(alias="date_planned_range", default=None)
    store_id__in: Optional[List[UUID4]] = Field(alias="store_id", default=None)
    order_type_id__in: Optional[List[UUID4]] = Field(alias="order_type_id", default=None)

    class Constants(Filter.Constants):
        model = Order
        ordering_field_name = "order_by"
        search_model_fields = ["external_number", "origin_number", "number"]



class OrderListSchema(GenericListSchema):
    data: Optional[List[OrderScheme]]
