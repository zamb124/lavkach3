from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.inventory.location.enums import PutawayStrategy
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.location.models import Location


class LocationBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    store_id: UUID4
    parent_id: Optional[UUID4] = None
    active: bool = None
    location_type_id: UUID4
    product_storage_type_ids: Optional[list[str]] = None
    partner_id: Optional[UUID4] = None
    homogeneity: Optional[bool] = None
    allow_create_package: Optional[bool] = None
    allowed_package_ids: Optional[list[UUID4]] = None
    exclusive_package_ids: Optional[list[UUID4]] = None
    allowed_order_types_ids: Optional[list[UUID4]] = None
    exclusive_order_types_ids: Optional[list[UUID4]] = None
    strategy: Optional[PutawayStrategy] = PutawayStrategy.FEFO


class LocationUpdateScheme(LocationBaseScheme):
    title: Optional[str] = None
    store_id: Optional[UUID4] = None
    location_type_id: Optional[UUID4] = None


class LocationCreateScheme(LocationBaseScheme):
    company_id: UUID4


class LocationScheme(LocationCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        orm_mode = True


class LocationFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at_lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at_lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str]
    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Location
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title"]


class LocationListSchema(GenericListSchema):
    data: Optional[List[LocationScheme]]
