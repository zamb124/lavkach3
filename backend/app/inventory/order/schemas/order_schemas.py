from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Any
from datetime import date

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, field_validator, model_validator, model_serializer
from pydantic.types import UUID4

from app.inventory.location.enums import PutawayStrategy

from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.order.models import Order
from app.inventory.order.models.order_models import OrderStatus
from app.inventory.order.schemas.order_type_schemas import OrderTypeScheme

class OrderBaseScheme(BaseModel):
    vars: Optional[dict] = None
    parent_id: Optional[UUID4] = None
    external_id: Optional[str] = None
    store_id: UUID4
    partner_id: Optional[UUID4] = None
    lot_id: Optional[UUID4] = None
    order_type_id: Optional[UUID4] = None
    origin_number: Optional[str] = None
    planned_date: Optional[datetime]
    actual_date: Optional[datetime]
    created_by: UUID4
    edited_by: UUID4
    expiration_date: Optional[datetime]
    users_ids: Optional[list[UUID4]] = []
    description: Optional[str]
    status: OrderStatus


class OrderUpdateScheme(OrderBaseScheme):
    vars: Optional[dict] = None
    external_id: Optional[str] = None
    lot_id: Optional[UUID4] = None
    origin_type: Optional[str] = None
    origin_number: Optional[str] = None
    planned_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
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
    moves: Optional[list[UUID4]] = []
    number: str
    order_type: 'OrderTypeScheme'

    class Config:
        orm_mode = True


def empty_erray(val):
    if val:
        return val

class OrderFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    planned_date__gte: Optional[datetime] = Field(description="bigger or equal planned date", default=None)
    planned_date__lt: Optional[datetime] = Field(description="less planned date", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    status__in: Optional[List[OrderStatus]] = Field(alias="status", default=None)
    date_planned_range: Optional[str] = Field(alias="date_planned_range", default=None)
    store_id__in: Optional[List[UUID4]] = None #Field(alias="store_id", default=None)
    order_type_id__in: Optional[List[UUID4]] = None #Field(alias="order_type_id", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str] = None

    @model_validator(mode="before")
    def check_root_validator(cls, value):
        """
            сериализует дейтрендж
        """
        if value.get('date_planned_range'):
            gte, lt = value['date_planned_range'].split(':')
            value.update({
                'planned_date__gte': datetime.fromisoformat(gte),
                'planned_date__lt': datetime.fromisoformat(f'{lt}T23:59:59')
            })
            value.pop('date_planned_range')
        return value

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Order
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["external_id", "origin_number", "number"]



class OrderListSchema(GenericListSchema):
    data: Optional[List[OrderScheme]]
