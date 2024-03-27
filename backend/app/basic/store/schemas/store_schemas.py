from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, field_validator
from pydantic.types import UUID
from app.basic.store.models.store_models import StoreType
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme
from app.basic.store.models.store_models import Store


class StoreBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str = Field(title='Title', table=True, form=True)
    external_number: Optional[str] = Field(default=None, title='External ID', table=True, form=True)
    address: Optional[str] = Field(default=None, title='Address', table=True, form=True)
    source: Optional[StoreType] = Field(default=StoreType.INTERNAL, title='Source', table=True, form=True)

    @field_validator('vars', mode='before')
    @classmethod
    def convert_int_serial(cls, v):
        if v == '':
            return {}
class StoreUpdateScheme(StoreBaseScheme):
    title: str = Field(default=None, title='Title', table=True, form=True)
    address: Optional[str] = Field(default=None, title='Address', table=True, form=True)
    source: Optional[StoreType] = Field(default=None, title='Source', table=True, form=True)


class StoreCreateScheme(StoreBaseScheme):
    pass


class StoreScheme(StoreCreateScheme, TimeStampScheme):
    company_id: UUID
    lsn: int
    id: UUID
    company_rel: Optional[CompanyScheme] = Field(table=True, form=True, title='Company')

    class Config:
        orm_mode = True


class StoreFilter(BaseFilter):
    title__in: Optional[List[str]] = Field(default=None, title='Title')
    address__in: Optional[List[str]] = Field(description="address", default=None)
    source__in: Optional[List[str]] = Field(default=None, title='Source', filter=True)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Store
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number", "address"]


class StoreListSchema(GenericListSchema):
    data: Optional[List[StoreScheme]]
