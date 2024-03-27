from datetime import datetime

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List

from core.schemas.timestamps import TimeStampScheme
from core.types.types import TypeCountry, TypeLocale, TypeCurrency
from fastapi_filter.contrib.sqlalchemy import Filter
from app.basic.company.models.company_models import Company
from core.schemas.list_schema import GenericListSchema
from core.schemas import BaseFilter


class CompanyBaseScheme(BaseModel):
    title: str = Field(title='Title', table=True, form=True)
    external_number: Optional[str] = Field(default=None, title='External ID', table=True, form=True)
    locale: Optional[TypeLocale] = Field(default=None, title='Locale', table=True, form=True)
    country: Optional[TypeCountry] = Field(default=None, title='Country', table=True, form=True)
    currency: TypeCurrency | str = Field(default=None, title='Currency', table=True, form=True)


class CompanyUpdateScheme(CompanyBaseScheme):
    currency: Optional[TypeCurrency | str]
    title: Optional[str]


class CompanyCreateScheme(CompanyBaseScheme):
    pass


class CompanyScheme(CompanyCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class CompanyFilter(BaseFilter):
    title__in: Optional[str] = Field(description="title", default=None)
    country__in: Optional[List[str]] = Field(default=None, filter=True)
    currency__in: Optional[List[str]] = Field(default=None, filter=True)
    locale__in: Optional[list[str]] = Field(default=None, filter=True)


    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Company
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number"]


class CompanyListSchema(GenericListSchema):
    data: Optional[List[CompanyScheme]]




