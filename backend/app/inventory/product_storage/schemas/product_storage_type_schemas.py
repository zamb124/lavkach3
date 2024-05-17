from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.inventory.product_storage.models.product_storage_models import ProductStorageType
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class ProductStorageTypeBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    external_number: Optional[str] = None

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = ProductStorageType

class ProductStorageTypeUpdateScheme(ProductStorageTypeBaseScheme):
    title: Optional[str] = None


class ProductStorageTypeCreateScheme(ProductStorageTypeBaseScheme):
    company_id: UUID4


class ProductStorageTypeScheme(ProductStorageTypeCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        from_attributes = True


class ProductStorageTypeFilter(BaseFilter):
    title__in: Optional[List[str]] = Field(description="title", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = ProductStorageType
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number"]


class ProductStorageTypeListSchema(GenericListSchema):
    data: Optional[List[ProductStorageTypeScheme]]
