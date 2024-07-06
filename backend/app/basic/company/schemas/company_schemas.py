from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4

from app.basic.company.models.company_models import Company
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from core.types.types import TypeCountry, TypeLocale, TypeCurrency


class CompanyBaseScheme(BasicModel):
    title: str = Field(title='Title', table=True, form=True)
    external_number: Optional[str] = Field(default=None, title='External ID', table=True, form=True)
    locale: Optional[TypeLocale] = Field(default='en_US', title='Locale', table=True, form=True, model='locale')
    country: Optional[TypeCountry] = Field(default='US', title='Country', table=True, form=True, model='country')
    currency: TypeCurrency | str = Field(default='USD', title='Currency', table=True, form=True, model='currency')

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Company
        service = 'app.basic.company.services.CompanyService'

class CompanyUpdateScheme(CompanyBaseScheme):
    ...


class CompanyCreateScheme(CompanyBaseScheme):
    pass


class CompanyScheme(CompanyCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int



class CompanyFilter(BaseFilter):
    title__in: Optional[str] = Field(description="title", default=None)
    country__in: Optional[List[TypeCountry]] = Field(default=None, model='country')
    currency__in: Optional[List[TypeCurrency]] = Field(default=None, model='currency')
    locale__in: Optional[list[TypeLocale]] = Field(default=None, model='locale')


    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Company
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number"]


class CompanyListSchema(GenericListSchema):
    data: Optional[List[CompanyScheme]]




