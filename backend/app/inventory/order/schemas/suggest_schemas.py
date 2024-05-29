from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.order.models import Suggest, SuggestType




class SuggestBaseScheme(BaseModel):
    move_id: UUID4 = Field(title='Move ID', model='move')
    priority: int = Field(title='Priority')
    type: SuggestType = Field(title='Type')
    value: Optional[str] = Field(default=None, title='Value')  # это значение которое или нужно заполнить или уже заполненное и нужно подвердить
    user_id: UUID4 = Field(default=None, title='User Done ID', model='user')

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Suggest

class SuggestUpdateScheme(SuggestBaseScheme):
    ...


class SuggestCreateScheme(SuggestBaseScheme):
    ...



class SuggestScheme(SuggestCreateScheme, TimeStampScheme):
    company_id: UUID4
    lsn: int
    id: UUID4

    class Config:
        from_attributes = True


class SuggestFilter(BaseFilter):
    move_id__in: Optional[List[UUID4]] = Field(default=None, title='Move')
    order_by: Optional[List[str]] = Field(default=["priority", ], title='Order by', filter=False)
    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Suggest
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["id", "move_id"]


class SuggestListSchema(GenericListSchema):
    data: Optional[List[SuggestScheme]]

