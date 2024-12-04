from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic.types import UUID4

from app.inventory.location.enums import LocationClass, PutawayStrategy
from app.inventory.location.models import LocationType
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel, bollean, BasicField as Field
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class LocationTypeBaseScheme(BasicModel):
    vars: Optional[dict] = None
    title: str = Field(title='Title', form=True, table=True)
    location_class: LocationClass = Field(title='Location Class', form=True, table=True)
    is_homogeneity: Optional[bool] = Field(default=False, title='Homogeneity', form=True, table=True)
    allowed_package_type_ids: Optional[list[UUID4]] = Field(
        default=[],
        model='location_type',
        filter={'location_class__in': LocationClass.PACKAGE.value},
        title='Allowed Package Types',
        form=True,
        table=True
    )
    exclude_package_type_ids: Optional[list[UUID4]] = Field(
        default=[],
        model='location_type',
        filter={'location_class__in': LocationClass.PACKAGE.value},
        title='Exclude Package Types',
        form=True,
        table=True
    )
    strategy: Optional[PutawayStrategy] = Field(default=PutawayStrategy.FEFO, title='Putaway Strategy', form=True,
                                                table=True)
    is_can_negative: bollean = Field(default=False, title='Can be Negative', form=True, table=True)

    class Config:
        orm_model = LocationType


class LocationTypeUpdateScheme(LocationTypeBaseScheme):
    title: Optional[str] = None
    location_class: Optional[LocationClass] = None


class LocationTypeCreateScheme(LocationTypeBaseScheme):
    ...


class LocationTypeScheme(LocationTypeCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4 = Field(title='ID', form=False, table=True)
    company_id: UUID4


class LocationTypeFilter(BaseFilter):
    location_class__in: Optional[List[LocationClass]] = Field(default=None, title='Location Class')
    allowed_package_type_ids__in: Optional[List[UUID4]] = Field(default=None, title='Allowed Package Types')

    class Constants(Filter.Constants):
        model = LocationType
        ordering_field_name = "order_by"
        search_model_fields = ["title", ]


class LocationTypeListSchema(GenericListSchema):
    data: Optional[List[LocationTypeScheme]]
