from typing import Optional, List

from celery.worker.strategy import default
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID

from ...bus.enums import BusStatus
from ....bus.bus.models.bus_models import Bus
from core.helpers.cache import CacheTag
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class BusBaseScheme(BasicModel):
    vars: Optional[dict] = None
    cache_tag: CacheTag = Field(title='Tag')
    message: str = Field(title='Message')
    status: BusStatus = Field(default=BusStatus.NEW, title='Status')
    company_id: UUID = Field(title='Company ID', model='company')
    user_id: Optional[UUID] = Field(default=None, title='User ID', model='user')

    class Config:
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
