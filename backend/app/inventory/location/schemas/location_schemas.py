from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.inventory.location.enums import PutawayStrategy
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.location.models import Location


class LocationBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    store_id: UUID4
    location_id: Optional[UUID4] = None
    is_active: bool = None
    location_type_id: UUID4
    partner_id: Optional[UUID4] = None



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
        from_attributes = True


class LocationFilter(BaseFilter):
    title__in: Optional[str] = Field(default=None)
    store_id__in: Optional[List[UUID4]] = Field(default=None, filter=True)
    is_active: Optional[bool] = Field(default=None, filter=True)
    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Location
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title"]


class LocationListSchema(GenericListSchema):
    data: Optional[List[LocationScheme]]
