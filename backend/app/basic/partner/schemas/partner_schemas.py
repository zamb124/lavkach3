from typing import List
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4

from app.basic.company.schemas.company_schemas import CompanyScheme
from app.basic.partner.models.partner_models import PartnerType, Partner
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from core.types.types import TypeCountry, TypePhone, TypeLocale, TypeCurrency


class PartnerBaseScheme(BasicModel):
    title: str = Field(title='Title', description="Title")
    type: PartnerType = Field(title='Type', description='')
    external_number: Optional[str] = Field(title='External ID')
    partner_id: Optional[str] = Field(model='partner')
    phone_number: Optional[TypePhone]
    email: Optional[str]
    locale: Optional[TypeLocale] = Field(default='en_US', title='Locale', table=True, form=True, model='locale')
    country: Optional[TypeCountry] = Field(default='US', title='Country', table=True, form=True, model='country')
    currency: TypeCurrency | str = Field(default='USD', title='Currency', table=True, form=True, model='currency')


    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Partner
        service = 'app.basic.partner.services.PartnerService'




class PartnerUpdateScheme(PartnerBaseScheme):
    pass


class PartnerCreateScheme(PartnerBaseScheme):
    pass

class PartnerParent(PartnerBaseScheme, TimeStampScheme):
    id: UUID4
    lsn: int


class PartnerScheme(PartnerParent, TimeStampScheme):
    partner_rel: Optional[PartnerParent]


class PartnerFilter(BaseFilter):
    title__in: Optional[str] = Field(default=None, title='Title')
    type__in: Optional[str] = Field(default=None, title='Type')
    external_number__in: Optional[str] = Field(default=None, title='External ID')
    partner_id__in: Optional[UUID4] = Field(default=None, title='Parent', model='partner')
    phone_number__in: Optional[str] = Field(default=None, title='Phone')
    email__in: Optional[str] = Field(default=None, title='Email')
    created_by: Optional[UUID4] = Field(default=None, title='User', model='user')
    country__in: Optional[List[TypeCountry]] = Field(default=None, model='country')
    currency__in: Optional[List[TypeCurrency]] = Field(default=None, model='currency')
    locale__in: Optional[list[TypeLocale]] = Field(default=None, model='locale')


    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Partner
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number", "email", "phone_number"]


class PartnerListSchema(GenericListSchema):
    data: Optional[List[CompanyScheme]]
