from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from app.basic.product.models.product_models import Product
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme
from app.basic.uom.schemas import UomScheme


class ProductBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    description: Optional[str] = None
    external_number: Optional[str] = None
    product_type: str = None
    uom_id: UUID4
    product_category_id: UUID4
    product_storage_type_id: UUID4
    barcode_list: list[str]

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Product
        service = 'app.basic.product.services.ProductService'


class ProductUpdateScheme(ProductBaseScheme):
    title: Optional[str] = None
    product_type: Optional[str] = None
    uom_id: UUID4 = None
    product_category_id: UUID4 = None
    product_storage_type_id: UUID4 = None
    barcode_list: Optional[list[str]] = None


class ProductCreateScheme(ProductBaseScheme):
    company_id: UUID4


class ProductScheme(ProductCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    uom_rel: UomScheme

    class Config:
        from_attributes = True


class ProductFilter(BaseFilter):
    title__in: Optional[List[str]] = Field(description="title", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Product
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number"]


class ProductListSchema(GenericListSchema):
    data: Optional[List[ProductScheme]]
