from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme
from app.inventory.quant.models import Quant


class QuantBaseScheme(BaseModel):
    company_id: UUID4
    vars: Optional[dict] = None
    product_id: UUID4
    location_id: UUID4
    lot_id: Optional[UUID4]
    owner_id: Optional[UUID4]
    quantity: float
    reserved_quantity: Optional[float]
    uom_id: UUID4


class QuantUpdateScheme(QuantBaseScheme):
    vars: Optional[dict] = None
    title: str = None
    external_id: str = None
    address: Optional[str] = None
    source: Optional[QuantType] = None


class QuantCreateScheme(QuantBaseScheme):
    pass


class QuantScheme(QuantCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company: Optional[CompanyScheme]

    class Config:
        orm_mode = True


class QuantFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id", default=0)
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at_lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at_lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    title__in: Optional[List[str]] = Field(description="title", default=None)
    address__in: Optional[List[str]] = Field(description="address", default=None)
    source__in: Optional[List[str]] = Field(description="source", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str] = None

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Quant
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_id", "address"]


class QuantListSchema(GenericListSchema):
    data: Optional[List[QuantScheme]]
