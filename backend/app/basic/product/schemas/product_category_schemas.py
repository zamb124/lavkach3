from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from app.basic.product.models.product_models import ProductCategory
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme


class ProductCategoryBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    external_number: Optional[str] = None
    parent_list_ids: Optional[list[UUID4]] = None


class ProductCategoryUpdateScheme(ProductCategoryBaseScheme):
    title: Optional[str] = None


class ProductCategoryCreateScheme(ProductCategoryBaseScheme):
    company_id: UUID4


class ProductCategoryScheme(ProductCategoryCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company_id: UUID4
    class Config:
        orm_mode = True


class ProductCategoryFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    title__in: Optional[List[str]] = Field(description="title", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str]

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = ProductCategory
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number"]


class ProductCategoryListSchema(GenericListSchema):
    data: Optional[List[ProductCategoryScheme]]
