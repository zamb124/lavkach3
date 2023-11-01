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
    vars: Optional[dict]
    title: str
    external_id: str
    address: Optional[str]
    source: Optional[StoreType]


class StoreUpdateScheme(StoreBaseScheme):
    pass


class StoreCreateScheme(StoreBaseScheme):
    pass


class StoreScheme(StoreCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company: Optional[CompanyScheme]

    class Config:
        from_attributes = True


class StoreFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id")
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created")
    created_at_lt: Optional[datetime] = Field(description="less created")
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated")
    updated_at_lt: Optional[datetime] = Field(description="less updated")
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id")
    title__in: Optional[List[str]] = Field(description="title")
    address__in: Optional[List[str]] = Field(description="address")
    source__in: Optional[List[str]] = Field(description="source")
    order_by: Optional[List[str]]
    search: Optional[str]

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Store
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_id", "address"]


class StoreListSchema(GenericListSchema):
    data: Optional[List[StoreScheme]]
