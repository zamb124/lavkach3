from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from app.basic.store.models.store_models import StoreType
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme
from app.basic.store.models.store_models import Store


class StoreBaseScheme(BaseModel):
    company_id: UUID4
    vars: Optional[dict] = None
    title: str
    external_id: Optional[str] = None
    address: Optional[str] = None
    source: Optional[StoreType] = StoreType.INTERNAL


class StoreUpdateScheme(StoreBaseScheme):
    company_id: Optional[UUID4] = None
    vars: Optional[dict] = None
    title: str = None
    address: Optional[str] = None
    source: Optional[StoreType] = None


class StoreCreateScheme(StoreBaseScheme):
    pass


class StoreScheme(StoreCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company: Optional[CompanyScheme]

    class Config:
        orm_mode = True


class StoreFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    title__in: Optional[List[str]] = Field(description="title", alias='title', default=None)
    address__in: Optional[List[str]] = Field(description="address", default=None)
    source__in: Optional[List[str]] = Field(description="source", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str] = None

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Store
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_id", "address"]


class StoreListSchema(GenericListSchema):
    data: Optional[List[StoreScheme]]
