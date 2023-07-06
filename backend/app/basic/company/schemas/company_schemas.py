from datetime import datetime

from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional, List

from core.schemas.timestamps import TimeStampScheme
from core.types.types import TypeCountry, TypeLocale, TypeCurrency
from fastapi_filter.contrib.sqlalchemy import Filter
from app.basic.company.models.company_models import Company
from core.schemas.list_schema import GenericListSchema
from core.helpers.fastapi_filter_patch import BaseFilter


class CompanyBaseScheme(BaseModel):
    title: str = Field(description="Title")
    external_id: Optional[str]
    locale: Optional[TypeLocale]
    country: Optional[TypeCountry]
    currency: TypeCurrency | str


class CompanyUpdateScheme(CompanyBaseScheme):
    currency: Optional[TypeCurrency | str]
    title: Optional[str]


class CompanyCreateScheme(CompanyBaseScheme):
    pass


class CompanyScheme(CompanyCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    country: TypeCountry
    locale: TypeLocale
    currency: TypeCurrency

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class CompanyFilter(BaseFilter):
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id")
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created")
    created_at_lt: Optional[datetime] = Field(description="less created")
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated")
    updated_at_lt: Optional[datetime] = Field(description="less updated")
    title__in: Optional[str] = Field(description="title")
    country__in: Optional[List[str]] = Field(alias="country")
    currency__in: Optional[List[str]] = Field(alias="currency")
    locale__in: Optional[List[str]] = Field(alias="locale")
    order_by: Optional[List[str]]
    search: Optional[str]

    class Config:
        allow_population_by_field_name = True

    class Constants(Filter.Constants):
        model = Company
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_id"]


class CompanyListSchema(GenericListSchema):
    data: Optional[List[CompanyScheme]]

