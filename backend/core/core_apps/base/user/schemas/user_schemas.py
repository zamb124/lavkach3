from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import UUID4

from ....base.company.schemas import CompanyCreateScheme, CompanyScheme
from ....base.user.models.user_models import UserType, User
from .....schemas import BaseFilter
from .....schemas.basic_schemes import BaseModel, BasicModel, BasicField as Field
from .....schemas.list_schema import GenericListSchema
from .....schemas.timestamps import TimeStampScheme
from .....types.types import *


class LoginResponseSchema(BasicModel):
    nickname: str
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
    user_id: Optional[UUID4]
    company_ids: Optional[List[UUID4]]
    company_id: Optional[UUID4] = None
    permission_list: Optional[List[str]]
    role_ids: Optional[List[str]]
    locale: Optional[str]
    country: Optional[str]

    class Config:
        orm_model = User

class UserBaseScheme(BaseModel):
    vars: Optional[dict] = {}
    email: str = Field(title="Email")
    locale: Optional[str] = Field(default='en_US', title='Locale', table=True, form=True, model='locale')
    country: Optional[str] = Field(default='US', title='Country', table=True, form=True, model='country')
    phone_number: Optional[str] = Field(default=None, title='Phone', table=True, form=True)
    nickname: str = Field(title='Nickname', table=True, form=True)
    is_admin: Optional[bool] = Field(default=False, title='Is Admin')
    type: Optional[UserType] = Field(default=UserType.COMMON, title='Type')
    external_number: Optional[str] = Field(default=None, title='External #', table=True)
    company_id: Optional[UUID4] = Field(default=None, title='Company Id', model='company')
    company_ids: Optional[list[UUID4]] = Field(default=None, title='Сompanies', model='company')
    role_ids: Optional[list[UUID4]] = Field(default=None, title='Roles', model='role')


class UserUpdateScheme(UserBaseScheme):
    email: str = Field(default=None, title="Email")


class UserCreateScheme(UserBaseScheme):
    password1: str = Field(..., description="Password1")
    password2: str = Field(..., description="Password2")
    password: Optional[str] = None
    # password: Optional[str]


class UserScheme(UserBaseScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    company_id: Optional[UUID4] = Field(title='Company Id', model='company')
    company_rel: Optional['CompanyScheme']
    locale: Optional[TypeLocale] = Field(default='en_US', title='Locale', table=True, form=True, model='locale')
    country: Optional[TypeCountry] = Field(default='US', title='Country', table=True, form=True, model='country')
    phone_number: Optional[TypePhone] = Field(default=None, title='Phone', table=True, form=True)


class UserFilter(BaseFilter):
    country__in: Optional[List[str]] = Field(alias="country", default=None)
    external_number__in: Optional[List[str]] = Field(default=None)
    email__in: Optional[List[str]] = Field(default=None)
    nickname__in: Optional[List[str]] = Field(default=None)
    role_ids__in: Optional[List[str]] = Field(default=None)
    locale__in: Optional[List[str]] = Field(default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = User
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["nickname", "email", "external_number"]


class UserListSchema(GenericListSchema):
    data: Optional[List[UserScheme]]


class SignUpScheme(BaseModel):
    user: 'UserCreateScheme'
    company: 'CompanyCreateScheme'


class ChangeCompanyScheme(BaseModel):
    user_id: UUID4
    company_id: UUID4

class ChangeLocaleScheme(BaseModel):
    user_id: UUID4
    locale: str
