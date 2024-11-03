from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, field_validator
from pydantic.types import UUID

from app.basic.store.models.store_models import Store
from app.basic.store.models.store_models import StoreType
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel, BasicField as Field
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class StoreBaseScheme(BasicModel):
    vars: Optional[dict] = None
    title: str = Field(title='Title', table=True, form=True)
    external_number: Optional[str] = Field(default=None, title='External ID', table=True, form=True)
    address: str = Field(title='Address', table=True, form=True)
    source: Optional[StoreType] = Field(default=StoreType.INTERNAL, title='Source', table=True, form=True)


    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Store
        service = 'app.basic.store.services.StoreService'

    @field_validator('vars', mode='before')
    @classmethod
    def convert_int_serial(cls, v):
        if v == '':
            return {}
class StoreUpdateScheme(StoreBaseScheme):
    title: str = Field(title='Title', table=True, form=True)
    source: Optional[StoreType] = Field(default=None, title='Source', table=True, form=True)


class StoreCreateScheme(StoreBaseScheme):
    pass


class StoreScheme(StoreCreateScheme, TimeStampScheme):
    company_id: UUID = Field(title='Company ID', model='company')
    lsn: int
    id: UUID = Field(title='ID', table=True)



class StoreFilter(BaseFilter):
    title__ilike: Optional[str] = Field(default=None, title='Title')
    address__ilike: Optional[str] = Field(description="address", default=None, title='Address')
    source__in: Optional[list[StoreType]] = Field(default=None, title='Source')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Store
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number", "address"]


class StoreListSchema(GenericListSchema):
    data: Optional[List[StoreScheme]]
