from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.quant.models import Quant


class QuantBaseScheme(BaseModel):
    vars: Optional[dict] = None
    product_id: UUID4
    store_id: UUID4
    location_id: Optional[UUID4] = None
    lot_id: Optional[UUID4] = None
    partner_id: Optional[UUID4] = None
    quantity: float
    reserved_quantity: Optional[float]
    expiration_date: Optional[datetime] = None
    uom_id: UUID4


class QuantUpdateScheme(QuantBaseScheme):
    store_id: Optional[UUID4] = None
    quantity: Optional[float] = None
    reserved_quantity: Optional[float] = None
    uom_id: Optional[UUID4] = None

class QuantCreateScheme(QuantBaseScheme):
    company_id: UUID4


class QuantScheme(QuantCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        orm_mode = True


class QuantFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Quant
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["company_id", "product_id", "lot_id"]


class QuantListSchema(GenericListSchema):
    data: Optional[List[QuantScheme]]
