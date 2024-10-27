from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field, UUID4

from ....base.company.schemas import CompanyCreateScheme, CompanyScheme
from ....base.user.models.user_models import UserType, User
from .....schemas import BaseFilter
from .....schemas.basic_schemes import BaseModel
from .....schemas.list_schema import GenericListSchema
from .....schemas.timestamps import TimeStampScheme
from .....types.types import *


class LoginResponseSchema(BaseModel):
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
        extra = 'allow'
        from_attributes = True
        orm_model = User
        service = 'app.base.user.services.UserService'

class UserBaseScheme(BaseModel):
    vars: Optional[dict] = {}
    email: str = Field(title="Email")
    locale: Optional[TypeLocale] = Field(default='en_US', title='Locale', table=True, form=True, model='locale')
    country: Optional[TypeCountry] = Field(default='US', title='Country', table=True, form=True, model='country')
    currency: TypeCurrency | str = Field(default='USD', title='Currency', table=True, form=True, model='currency')
    phone_number: Optional[TypePhone] = Field(default=None, title='Phone', table=True, form=True)
    nickname: str = Field(title='Nickname', table=True, form=True)
    is_admin: Optional[bool] = Field(default=False, title='Is Admin')
    type: Optional[UserType] = Field(default=UserType.COMMON, title='Type')
    external_number: Optional[str] = Field(default=False, title='External #', table=True)
    company_ids: Optional[list[UUID4]] = Field(default=None, title='Сompanies', model='company')
    role_ids: Optional[list[UUID4]] = Field(default=None, title='Roles', model='role')


class UserUpdateScheme(UserBaseScheme):
    ...


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
