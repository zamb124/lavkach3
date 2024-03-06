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
    company_id: UUID4
    vars: Optional[dict] = None
    title: str
    external_id: Optional[str] = None
    parent_id: Optional[UUID4] = None


class ProductCategoryUpdateScheme(ProductCategoryBaseScheme):
    title: Optional[str] = None


class ProductCategoryCreateScheme(ProductCategoryBaseScheme):
    pass


class ProductCategoryScheme(ProductCategoryCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company: Optional[CompanyScheme]

    class Config:
        orm_mode = True


class ProductCategoryFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id")
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created")
    created_at_lt: Optional[datetime] = Field(description="less created")
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated")
    updated_at_lt: Optional[datetime] = Field(description="less updated")
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id")
    title__in: Optional[List[str]] = Field(description="title")
    order_by: Optional[List[str]]
    search: Optional[str]

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = ProductCategory
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_id"]


class ProductCategoryListSchema(GenericListSchema):
    data: Optional[List[ProductCategoryScheme]]
