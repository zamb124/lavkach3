from datetime import datetime

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List

from core.schemas.timestamps import TimeStampScheme
from core.types.types import TypeCountry, TypeLocale, TypeCurrency
from fastapi_filter.contrib.sqlalchemy import Filter
from app.basic.company.models.company_models import Company
from core.schemas.list_schema import GenericListSchema
from core.helpers.fastapi_filter_patch import BaseFilter


class CompanyBaseScheme(BaseModel):
    title: str = Field(description="Title")
    external_id: Optional[str] = None
    locale: Optional[TypeLocale] = None
    country: Optional[TypeCountry] = None
    currency: TypeCurrency | str = None


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
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    title__in: Optional[str] = Field(description="title", default=None)
    country__in: Optional[List[str]] = Field(alias="country", default=None)
    currency__in: Optional[List[str]] = Field(alias="currency", default=None)
    locale__in: Optional[List[str]] = Field(alias="locale", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str] = None

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Company
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_id"]


class CompanyListSchema(GenericListSchema):
    data: Optional[List[CompanyScheme]]

