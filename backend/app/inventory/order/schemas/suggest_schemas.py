from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, computed_field
from pydantic.types import UUID4

from app.inventory.order.models import Suggest, SuggestType
from core.schemas import BaseFilter
from core.schemas.basic_schemes import ActionBaseSchame
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class SuggestBaseScheme(BaseModel):
    move_id: UUID4 = Field(title='Move ID', model='move', readonly=True)
    priority: int = Field(title='Priority', readonly=True)
    type: SuggestType = Field(title='Type', readonly=True)
    value: Optional[str] = Field(default=None, title='Value', readonly=True)  # это значение которое или нужно заполнить или уже заполненное и нужно подвердить
    user_id: Optional[UUID4] = Field(default=None, title='User Done ID', model='user', readonly=True)

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Suggest

class SuggestUpdateScheme(SuggestBaseScheme):
    ...


class SuggestCreateScheme(SuggestBaseScheme):
    ...



class SuggestScheme(SuggestCreateScheme, TimeStampScheme):
    company_id: UUID4 = Field(title='Company ID', model='company')
    lsn: int
    id: UUID4

    @computed_field
    @property
    def title(self) -> str:
        return f'[{self.type.name}] - {self.priority}'


class SuggestFilter(BaseFilter):
    move_id__in: Optional[List[UUID4]] = Field(default=None, title='Move')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Suggest
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["id", "move_id"]


class SuggestListSchema(GenericListSchema):
    data: Optional[List[SuggestScheme]]


class SuggestConfirmScheme(ActionBaseSchame):
    value: str = Field(title='Value', readonly=False)
    barcode: Optional[str] = Field(default='', title='Barcode')

