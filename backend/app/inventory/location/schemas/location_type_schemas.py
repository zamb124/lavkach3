from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.inventory.location.enums import LocationClass, PutawayStrategy
from app.inventory.location.models import LocationType
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel, bollean
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class LocationTypeBaseScheme(BasicModel):
    vars: Optional[dict] = None
    title: str
    location_class: LocationClass
    is_homogeneity: Optional[bool] = None
    allowed_package_ids: Optional[list[UUID4]] = Field(default=[], module='inventory', model='location', filter={'location_class__in': LocationClass.PACKAGE})
    exclude_package_ids: Optional[list[UUID4]] = Field(default=[], module='inventory', model='location', filter={'location_class__in': LocationClass.PACKAGE})
    strategy: Optional[PutawayStrategy] = PutawayStrategy.FEFO
    is_can_negative: bollean = Field(default=False, title='Can be Negative')

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = LocationType

class LocationTypeUpdateScheme(LocationTypeBaseScheme):
    title: Optional[str] = None
    location_class: Optional[LocationClass] = None


class LocationTypeCreateScheme(LocationTypeBaseScheme):
    company_id: UUID4


class LocationTypeScheme(LocationTypeCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4



class LocationTypeFilter(BaseFilter):
    ...


    class Constants(Filter.Constants):
        model = LocationType
        ordering_field_name = "order_by"
        search_model_fields = ["title",]


class LocationTypeListSchema(GenericListSchema):
    data: Optional[List[LocationTypeScheme]]
