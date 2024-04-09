from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from app.basic.product.models.product_models import ProductCategory
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme


class ProductCategoryBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    external_number: Optional[str] = None
    product_category_ids: Optional[list[UUID4]] = None


class ProductCategoryUpdateScheme(ProductCategoryBaseScheme):
    title: Optional[str] = None


class ProductCategoryCreateScheme(ProductCategoryBaseScheme):
    company_id: UUID4


class ProductCategoryScheme(ProductCategoryCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company_id: UUID4
    class Config:
        from_attributes = True


class ProductCategoryFilter(BaseFilter):
    title__in: Optional[List[str]] = Field(description="title", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = ProductCategory
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number"]


class ProductCategoryListSchema(GenericListSchema):
    data: Optional[List[ProductCategoryScheme]]
