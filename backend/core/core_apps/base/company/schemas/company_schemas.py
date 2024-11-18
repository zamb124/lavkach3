from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field, UUID4

from ....base.company.models.company_models import Company
from .....schemas import BaseFilter
from .....schemas.basic_schemes import BasicModel
from .....schemas.list_schema import GenericListSchema
from .....schemas.timestamps import TimeStampScheme
from .....types.types import TypeCountry, TypeLocale, TypeCurrency


class CompanyBaseScheme(BasicModel):
    title: str = Field(title='Title', table=True, form=True)
    external_number: Optional[str] = Field(default=None, title='External ID', table=True, form=True)
    locale: Optional[TypeLocale] = Field(default='en_US', title='Locale', table=True, form=True, model='locale')
    country: Optional[TypeCountry] = Field(default='US', title='Country', table=True, form=True, model='country')
    currency: TypeCurrency = Field(default='USD', title='Currency', table=True, form=True, model='currency')

    class Config:
        orm_model = Company

class CompanyUpdateScheme(CompanyBaseScheme):
    ...


class CompanyCreateScheme(CompanyBaseScheme):
    pass


class CompanyScheme(CompanyCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int



class CompanyFilter(BaseFilter):
    title__in: Optional[str] = Field(description="title", default=None)
    country__in: Optional[list[str]] = Field(default=None, model='country')
    currency__in: Optional[list[str]] = Field(default=None, model='currency')
    locale__in: Optional[list[str]] = Field(default=None, model='locale')


    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Company
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number"]


class CompanyListSchema(GenericListSchema):
    data: Optional[List[CompanyScheme]]




