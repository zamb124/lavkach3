from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.location.models import LocationType
from app.inventory.location.enums import LocationClass, PutawayStrategy


class LocationTypeBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    location_class: LocationClass
    homogeneity: Optional[bool] = None
    mix_products: Optional[bool] = None
    allow_create_package: Optional[bool] = None
    allowed_package_ids: Optional[list[UUID4]] = None
    exclusive_package_ids: Optional[list[UUID4]] = None
    allowed_order_types_ids: Optional[list[UUID4]] = None
    exclusive_order_types_ids: Optional[list[UUID4]] = None
    strategy: Optional[PutawayStrategy] = PutawayStrategy.FEFO
    product_storage_type_ids: Optional[list[str]] = None

class LocationTypeUpdateScheme(LocationTypeBaseScheme):
    title: Optional[str] = None
    location_class: Optional[LocationClass] = None


class LocationTypeCreateScheme(LocationTypeBaseScheme):
    company_id: UUID4


class LocationTypeScheme(LocationTypeCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        orm_mode = True


class LocationTypeFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = LocationType
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title",]


class LocationTypeListSchema(GenericListSchema):
    data: Optional[List[LocationTypeScheme]]
