from datetime import datetime
from typing import List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4
from typing import Optional

from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from core.types.types import TypeCountry, TypePhone, TypeLocale, TypeCurrency
from app.basic.partner.models.partner_models import PartnerType, Partner
from app.basic.company.schemas.company_schemas import CompanyScheme
from enum import Enum
class PartnerBaseScheme(BaseModel):
    company_id: UUID4
    title: str = Field(description="Title")
    type: PartnerType
    external_number: Optional[str]
    partner_id: Optional[str]
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
    company_id: CompanyScheme
    locale: TypeLocale
    currency: TypeCurrency

class PartnerScheme(PartnerParent, TimeStampScheme):
    partner_rel: Optional[PartnerParent]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class PartnerFilter(BaseFilter):
    title__in: Optional[str] = Field(default=None, title='Title')
    type__in: Optional[str] = Field(default=None, title='Type')
    external_number__in: Optional[str] = Field(default=None, title='External ID')
    partner_id__in: Optional[UUID4] = Field(default=None, title='Parent')
    phone_number__in: Optional[str] = Field(default=None, title='Phone')
    email__in: Optional[str] = Field(default=None, title='Email')
    created_user_id__in: Optional[UUID4] = Field(default=None, title='User')
    country__in: Optional[List[str]] = Field(default=None, title='Country')
    currency__in: Optional[List[str]] = Field( default=None, title='Currency')
    locale__in: Optional[List[str]] = Field(default=None, title='Locale')


    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Partner
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number", "email", "phone_number"]


class PartnerListSchema(GenericListSchema):
    data: Optional[List[CompanyScheme]]
