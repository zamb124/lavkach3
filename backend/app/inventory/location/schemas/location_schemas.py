from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic.types import UUID4
from core.schemas.basic_schemes import BasicField as Field, bollean

from app.inventory.location.enums import LocationClass
from app.inventory.location.models import Location
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class LocationBaseScheme(BasicModel):
    vars: Optional[dict] = None
    location_class: LocationClass
    title: str
    store_id: UUID4 = Field(title='Store', model='store')
    location_id: Optional[UUID4] = Field(default=None, title='Parent Location', model='location')
    is_active: bollean = Field(default=True, title='Is Active')
    location_type_id: UUID4 = Field(title='Location Type', model='location_type')
    partner_id: Optional[UUID4] = Field(default=None, title='Partner', model='partner')

    location_class: LocationClass = Field(default=LocationClass.PLACE, title='Location Class')
    is_can_negative: bollean = Field(default=False, title='Can Negative')
    allowed_package_type_ids: Optional[list[UUID4]] = Field(
        default=[], title='Allowed Packages',
        filter={'location_class__in': LocationClass.PACKAGE.value}
    )  # Разрешенные типы упаковок
    exclude_package_type_ids: Optional[list[UUID4]] = Field(
        default=[], title='Exclude Packages',
        filter={'location_class__in': LocationClass.PACKAGE.value}
    )  # Разрешенные типы упаковок

    class Config:
        orm_model = Location

class LocationUpdateScheme(LocationBaseScheme):
    ...


class LocationCreateScheme(LocationBaseScheme):
    ...


class LocationScheme(LocationCreateScheme, TimeStampScheme):
    company_id: UUID4 = Field(model='company', title='Company')
    lsn: int
    id: UUID4

    class Config:
        from_attributes = True


class LocationFilter(BaseFilter):
    title: Optional[str] = Field(default=None, title='Title')
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store', model='store')
    location_type_id__in: Optional[List[UUID4]] = Field(default=None, title='Location Type', model='location_type')
    location_class__in: Optional[List[LocationClass]] = Field(default=None, title='Class')
    location_class__not_in: Optional[List[LocationClass]] = Field(default=None, title='Class')
    is_active: Optional[bool] = Field(default=None, title='Active')
    is_can_negative: Optional[bool] = Field(default=None, title='Is can negative')

    class Constants(Filter.Constants):
        model = Location
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title"]


class LocationListSchema(GenericListSchema):
    data: Optional[List[LocationScheme]]
