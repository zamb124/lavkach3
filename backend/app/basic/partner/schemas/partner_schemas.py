from datetime import datetime
from typing import List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional

from core.helpers.fastapi_filter_patch import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from core.types.types import TypeCountry, TypePhone, TypeLocale, TypeCurrency
from app.basic.partner.models.partner_models import PartnerType, Partner
from app.basic.company.schemas.company_schemas import CompanyScheme
class PartnerBaseScheme(BaseModel):
    company_id: UUID4
    title: str = Field(description="Title")
    type: PartnerType
    external_id: Optional[str]
    parent_id: Optional[str]
    phone_number: Optional[TypePhone]
    email: Optional[str]
    country: Optional[TypeCountry]
    locale: Optional[TypeLocale]
    currency: Optional[TypeCurrency]


class PartnerUpdateScheme(PartnerBaseScheme):
    pass


class PartnerCreateScheme(PartnerBaseScheme):
    pass

class PartnerParent(PartnerBaseScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    country: TypeCountry
    company_id = CompanyScheme
    locale: TypeLocale
    currency: TypeCurrency

class PartnerScheme(PartnerParent, TimeStampScheme):
    partner: Optional[PartnerParent]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class PartnerFilter(BaseFilter):
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id")
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created")
    created_at_lt: Optional[datetime] = Field(description="less created")
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated")
    updated_at_lt: Optional[datetime] = Field(description="less updated")
    title__in: Optional[str] = Field(description="title")
    type__in: Optional[str] = Field(description="type")
    external_id__in: Optional[str] = Field(description="external_id")
    parent_id__in: Optional[UUID4] = Field(description="parent_id")
    phone_number__in: Optional[str] = Field(description="phone_number")
    email__in: Optional[str] = Field(description="email")
    created_user_id__in: Optional[str] = Field(description="created_user_id")

    country__in: Optional[List[str]] = Field(alias="country")
    currency__in: Optional[List[str]] = Field(alias="currency")
    locale__in: Optional[List[str]] = Field(alias="locale")
    order_by: Optional[List[str]]
    search: Optional[str]


    class Config:
        allow_population_by_field_name = True

    class Constants(Filter.Constants):
        model = Partner
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_id", "email", "phone_number"]


class PartnerListSchema(GenericListSchema):
    data: Optional[List[CompanyScheme]]
