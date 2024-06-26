from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID

from app.bus.bus.enums import BusStatus
from app.bus.bus.models.bus_models import Bus
from core.helpers.cache import CacheTag
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class BusBaseScheme(BaseModel):
    vars: Optional[dict] = None
    cache_tag: CacheTag = Field(title='Tag')
    message: str = Field(title='Message')
    status: BusStatus = Field(default=BusStatus.NEW, title='Status')
    company_id: UUID = Field(title='Company ID', model='company')

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Bus
class BusUpdateScheme(BusBaseScheme):
    ...


class BusCreateScheme(BusBaseScheme):
    ...


class BusScheme(BusCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID



class BusFilter(BaseFilter):
    cache_tag: Optional[CacheTag] = Field(default=None, title='Tag')
    status__in: Optional[list[BusStatus]] = Field(default=None,title='Status')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Bus
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["cache_tag"]


class BusListSchema(GenericListSchema):
    data: Optional[List[BusScheme]]
