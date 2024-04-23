from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.location.models import LocationType
from app.inventory.location.enums import LocationClass, PutawayStrategy


class LocationTypeBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str
    location_class: LocationClass
    is_homogeneity: Optional[bool] = None
    is_mix_products: Optional[bool] = None
    is_allow_create_package: Optional[bool] = None
    allowed_package_ids: Optional[list[UUID4]] = Field(default=None, module='inventory', model='location_id', filter={'location_class__in': 'package'})
    exclusive_package_ids: Optional[list[UUID4]] = Field(default=None, module='inventory', model='location_id', filter={'location_class__in': 'package'})
    allowed_order_type_ids: Optional[list[UUID4]] = Field(default=None, module='inventory', model='order_type')
    exclusive_order_type_ids: Optional[list[UUID4]] = Field(default=None, module='inventory', model='order_type')
    strategy: Optional[PutawayStrategy] = PutawayStrategy.FEFO
    product_storage_type_ids: Optional[list[str]] = None

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = LocationType
        service = 'app.inventory.location.services.LocationTypeService'

class LocationTypeUpdateScheme(LocationTypeBaseScheme):
    title: Optional[str] = None
    location_class: Optional[LocationClass] = None


class LocationTypeCreateScheme(LocationTypeBaseScheme):
    company_id: UUID4


class LocationTypeScheme(LocationTypeCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        from_attributes = True


class LocationTypeFilter(BaseFilter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = LocationType
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title",]


class LocationTypeListSchema(GenericListSchema):
    data: Optional[List[LocationTypeScheme]]
