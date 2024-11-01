from typing import Optional, List
from uuid import UUID

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import computed_field
from pydantic.types import UUID4

from app.inventory.store_staff.enums import StaffPosition
from core.schemas.basic_schemes import BasicField as Field, bollean

from app.inventory.store_staff.models import StoreStaff
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class StoreStaffBaseScheme(BasicModel):
    vars: Optional[dict] = None
    user_id: UUID = Field(title='User', model='user', table=True, form=True)
    staff_position: StaffPosition = Field(default=StaffPosition.STOREKEEPER, title='Staff Position', table=True, form=True)
    store_id: UUID4 = Field(title='Store', model='store', table=True, form=True)
    store_ids: Optional[list[UUID4]] = Field(default=[],model='store', title='Stores', table=True, form=True)  # Разрешенные типы упаковок
    staff_number: Optional[str] = Field(default=None, title='Staff ID', table=True, form=True)
    external_number: Optional[str] = Field(default=None, title='External ID', table=True, form=True)

    class Config:
        orm_model = StoreStaff

class StoreStaffUpdateScheme(StoreStaffBaseScheme):
    ...


class StoreStaffCreateScheme(StoreStaffBaseScheme):
    ...


class StoreStaffScheme(StoreStaffCreateScheme, TimeStampScheme):
    company_id: UUID4 = Field(model='company', title='Company')
    lsn: int
    id: UUID4 = Field(title='ID', table=True)

    @computed_field(title='Order #', json_schema_extra={'table': True})
    def title(self) -> str:
        "some title"
        return f'{self.staff_position.value}'

class StoreStaffFilter(BaseFilter):
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store', model='store')
    user_id__in: Optional[List[UUID4]] = Field(default=None, title='User Inn', model='user')
    staff_position__in: Optional[List[StaffPosition]] = Field(default=None, title='Class')
    staff_position__not_in: Optional[List[StaffPosition]] = Field(default=None, title='Class')

    class Constants(Filter.Constants):
        model = StoreStaff
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["staff_number", "external_number"]


class StoreStaffListSchema(GenericListSchema):
    data: Optional[List[StoreStaffScheme]]
