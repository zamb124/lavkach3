from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.inventory.location.enums import PutawayStrategy, LocationClass
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.location.models import Location


class LocationBaseScheme(BaseModel):
    vars: Optional[dict] = None
    location_class: LocationClass
    title: str
    store_id: UUID4
    location_id: Optional[UUID4] = None
    is_active: bool = None
    location_type_id: UUID4
    partner_id: Optional[UUID4] = None

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Location
        service = 'app.inventory.location.services.LocationService'

class LocationUpdateScheme(LocationBaseScheme):
    ...


class LocationCreateScheme(LocationBaseScheme):
    ...


class LocationScheme(LocationCreateScheme, TimeStampScheme):
    company_id: UUID4
    lsn: int
    id: UUID4

    class Config:
        from_attributes = True


class LocationFilter(BaseFilter):
    title__in: Optional[str] = Field(default=None, title='Title')
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store')
    location_class__in: Optional[List[str]] = Field(default=None, title='Class')
    is_active: Optional[bool] = Field(default=None, title='Active')
    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Location
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title"]


class LocationListSchema(GenericListSchema):
    data: Optional[List[LocationScheme]]
