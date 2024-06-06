from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.basic.product.models.product_models import ProductCategory
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class ProductCategoryBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str = Field(title='Title')
    external_number: Optional[str] = Field(default=None, title='External ID')
    product_category_ids: Optional[list[UUID4]] = Field(default=[], title="Child categories", model='product_category')

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = ProductCategory
        service = 'app.basic.product.services.ProductCategoryService'


class ProductCategoryUpdateScheme(ProductCategoryBaseScheme):
    ...


class ProductCategoryCreateScheme(ProductCategoryBaseScheme):
    ...


class ProductCategoryScheme(ProductCategoryCreateScheme, TimeStampScheme):
    lsn: int = Field(table=False)
    id: UUID4 = Field(table=False)
    company_id: UUID4 = Field(title='Company', model='company')


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
