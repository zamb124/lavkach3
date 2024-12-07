from typing import Optional, List, Union, Any

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic.types import UUID4

from app.inventory.location.enums import LocationClass, BlockerEnum
from app.inventory.location.models import Location
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicField as Field, bollean
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from sqlalchemy.orm import Query, aliased
from sqlalchemy.sql.selectable import Select


class LocationBaseScheme(BasicModel):
    vars: Optional[dict] = None
    title: str = Field(title='Title', form=True, table=True)
    store_id: UUID4 = Field(title='Store', model='store', form=True, table=True)
    is_active: bollean = Field(default=True, title='Is Active', form=True, table=True)
    location_class: LocationClass = Field(title='Location Class', form=True, table=True)
    location_type_id: UUID4 = Field(title='Location Type', model='location_type', form=True, table=True)
    location_id: Optional[UUID4] = Field(default=None, title='Parent Location', model='location', form=True, table=True)
    block: BlockerEnum = Field(default=BlockerEnum.FREE, title='Block', form=True, table=True)
    sort: int = Field(default=0, title='Sort', form=True, table=True)

    class Config:
        orm_model = Location


class LocationUpdateScheme(LocationBaseScheme):
    ...


class LocationCreateScheme(LocationBaseScheme):
    ...


class LocationScheme(LocationCreateScheme, TimeStampScheme):
    company_id: UUID4 = Field(model='company', title='Company', form=True, table=True)
    lsn: int
    id: UUID4 = Field(title='ID', form=True, table=True)


class LocationFilter(BaseFilter):
    title: Optional[str] = Field(default=None, title='Title')
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store', model='store')
    location_type_id__in: Optional[List[UUID4]] = Field(default=None, title='Location Type', model='location_type')
    location_class__in: Optional[List[LocationClass]] = Field(default=None, title='Location Class')
    location_id__in: Optional[List[UUID4]] = Field(default=None, title='Zone', model='location')
    location_id__isnull: Optional[bool] = Field(default=None, title='Parent Location')
    is_active: Optional[bool] = Field(default=None, title='Active')
    zone_id__in: Optional[List[UUID4]] = Field(default=None, title='Zone', model='location')

    class Constants(Filter.Constants):
        model = Location
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title"]

    def filter(self, query: Union[Query, Select]):
        if self.zone_id__in:
            query = Location.get_query_locations_by_zone_ids(self.zone_id__in)
        if hasattr(self, 'zone_id__in'):
            del self.zone_id__in
        return super().filter(query)


class LocationListSchema(GenericListSchema):
    data: Optional[List[LocationScheme]]


class GetLocationTreeSchema(BasicModel):
    location_ids: List[UUID4]


class LocationTreeSchema(LocationScheme):
    child_locations_rel: Optional[List['LocationTreeSchema']] = Field(default=None, title='Child Locations')

class UpdateParent(BasicModel):
    id: UUID4 = Field(title='ID', form=True, table=True)
    parent_id: Optional[UUID4] = Field(default=None, title='Parent Location', model='location', form=True, table=True)