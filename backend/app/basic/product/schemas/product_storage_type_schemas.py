from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from app.basic.product.models.product_models import ProductStorageType
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme


class ProductStorageTypeBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    external_id: Optional[str] = None


class ProductStorageTypeUpdateScheme(ProductStorageTypeBaseScheme):
    title: Optional[str] = None


class ProductStorageTypeCreateScheme(ProductStorageTypeBaseScheme):
    company_id: UUID4


class ProductStorageTypeScheme(ProductStorageTypeCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        orm_mode = True


class ProductStorageTypeFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at_lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at_lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    title__in: Optional[List[str]] = Field(description="title", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str]

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = ProductStorageType
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_id"]


class ProductStorageTypeListSchema(GenericListSchema):
    data: Optional[List[ProductStorageTypeScheme]]
