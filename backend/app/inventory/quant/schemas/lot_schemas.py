from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.quant.models import Lot


class LotBaseScheme(BaseModel):
    vars: Optional[dict] = None
    expiration_date: Optional[datetime] = None
    product_id: UUID4
    external_id: Optional[str] = None
    partner_id: Optional[UUID4] = None


class LotUpdateScheme(LotBaseScheme):
    pass


class LotCreateScheme(LotBaseScheme):
    company_id: UUID4


class LotScheme(LotCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        orm_mode = True


class LotFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str]
    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Lot
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["external_id"]


class LotListSchema(GenericListSchema):
    data: Optional[List[LotScheme]]
