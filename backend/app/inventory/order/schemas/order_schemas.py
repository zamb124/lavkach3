from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.inventory.location.enums import PutawayStrategy
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.order.models import Order, OrderType
from app.inventory.order.models.order_models import OrderStatus, OrderClass, BackOrderAction, ReservationMethod


class OrderBaseScheme(BaseModel):
    company_id: UUID4
    vars: Optional[dict] = None
    parent_id: Optional[UUID4] = None
    external_id: Optional[str] = None
    store_id: UUID4
    partner_id: Optional[UUID4] = None
    lot_id: UUID4 = None
    origin_type: Optional[str] = None
    origin_number: Optional[str] = None
    planned_date: Optional[datetime]
    actual_date: Optional[datetime]
    created_by: UUID4
    edited_by: UUID4
    expiration_date: Optional[datetime]
    users_ids: Optional[list[UUID4]] = []
    description: Optional[str]
    status: OrderStatus
    moves: Optional[list[UUID4]] = []


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

class OrderCreateScheme(OrderBaseScheme):
    pass


class OrderScheme(OrderCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company: UUID4

    class Config:
        orm_mode = True


class OrderFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at_lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at_lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    store_id__in: Optional[List[UUID4]] = Field(alias="store_id", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Order
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["company_id", "product_id", "lot_id"]


class OrderListSchema(GenericListSchema):
    data: Optional[List[OrderScheme]]

