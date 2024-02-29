from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.location.models import Location


class LocationBaseScheme(BaseModel):
    company_id: UUID4
    vars: Optional[dict] = None
    title: str
    store_id: UUID4
    parent_id: Optional[UUID4]
    active: bool
    location_type_id: UUID4
    product_storage_type_ids: Optional[list[str]]
    partner_id: Optional[UUID4]


class LocationUpdateScheme(LocationBaseScheme):
    vars: Optional[dict] = None
    title: Optional[str]
    store_id: Optional[UUID4]
    parent_id: Optional[UUID4]
    active: Optional[bool]
    location_type_id: Optional[UUID4]
    product_storage_type_ids: Optional[list[str]]
    partner_id: Optional[UUID4]


class LocationCreateScheme(LocationBaseScheme):
    pass


class LocationScheme(LocationCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    company: UUID4

    class Config:
        orm_mode = True


class LocationFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id", default=0)
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at_lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at_lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Location
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["company_id", "store_id", "partner_id"]


class LocationListSchema(GenericListSchema):
    data: Optional[List[LocationScheme]]
