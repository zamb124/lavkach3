from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic.types import UUID4
from core.schemas.basic_schemes import BasicField as Field, bollean

from app.inventory.store_staff.enums import StoreStaffClass
from app.inventory.store_staff.models import StoreStaff
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class StoreStaffBaseScheme(BasicModel):
    vars: Optional[dict] = None
    store_staff_class: StoreStaffClass
    title: str
    store_id: UUID4 = Field(title='Store', model='store')
    store_staff_id: Optional[UUID4] = Field(default=None, title='Parent StoreStaff', model='store_staff')
    is_active: bollean = Field(default=True, title='Is Active')
    store_staff_type_id: UUID4 = Field(title='StoreStaff Type', model='store_staff_type')
    partner_id: Optional[UUID4] = Field(default=None, title='Partner', model='partner')

    store_staff_class: StoreStaffClass = Field(default=StoreStaffClass.PLACE, title='StoreStaff Class')
    lot_id: Optional[UUID4] = Field(default=None, title='Lot')
    is_can_negative: bollean = Field(default=False, title='Can Negative')
    allowed_package_ids: Optional[list[UUID4]] = Field(default=[], title='Allowed Packages')  # Разрешенные типы упаковок
    exclude_package_ids: Optional[list[UUID4]] = Field(default=[], title='Exclude Packages')  # Разрешенные типы упаковок

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = StoreStaff

class StoreStaffUpdateScheme(StoreStaffBaseScheme):
    ...


class StoreStaffCreateScheme(StoreStaffBaseScheme):
    ...


class StoreStaffScheme(StoreStaffCreateScheme, TimeStampScheme):
    company_id: UUID4 = Field(model='company', title='Company')
    lsn: int
    id: UUID4

    class Config:
        from_attributes = True


class StoreStaffFilter(BaseFilter):
    title: Optional[str] = Field(default=None, title='Title')
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store', model='store')
    store_staff_type_id__in: Optional[List[UUID4]] = Field(default=None, title='StoreStaff Type', model='store_staff_type')
    store_staff_class__in: Optional[List[StoreStaffClass]] = Field(default=None, title='Class')
    store_staff_class__not_in: Optional[List[StoreStaffClass]] = Field(default=None, title='Class')
    is_active: Optional[bool] = Field(default=None, title='Active')
    is_can_negative: Optional[bool] = Field(default=None, title='Is can negative')

    class Constants(Filter.Constants):
        model = StoreStaff
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title"]


class StoreStaffListSchema(GenericListSchema):
    data: Optional[List[StoreStaffScheme]]
