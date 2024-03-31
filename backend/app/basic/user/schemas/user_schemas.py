from datetime import datetime

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List

from app.basic.company.schemas import CompanyCreateScheme, CompanyScheme
from app.basic.user.models.user_models import UserType, User
from app.basic.store.schemas.store_schemas import StoreScheme
from core.schemas import BaseFilter
from core.schemas.timestamps import TimeStampScheme
from core.types.types import *
from core.schemas.list_schema import GenericListSchema


class LoginResponseSchema(BaseModel):
    nickname: str
    store_id: Optional[UUID4]
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
    user_id: Optional[UUID4]
    company_ids: Optional[List[UUID4]]
    company_id: Optional[UUID4] = None
    permission_list: Optional[List[str]]
    role_ids: Optional[List[str]]
    locale: Optional[str]
    country: Optional[str]


class UserBaseScheme(BaseModel):
    vars: Optional[dict] = {}
    email: str = Field(title="Email")
    country: Optional[TypeCountry] = Field(default=None, title='Country', table=True, form=True)
    locale: TypeLocale = Field(default=None, title='Locale', table=True, form=True)
    phone_number: Optional[TypePhone] = Field(default=None, title='Phone', table=True, form=True)
    nickname: str = Field(title='Nickname', table=True, form=True)
    is_admin: Optional[bool] = Field(default=False, title='Is Admin')
    type: Optional[UserType] = Field(default=UserType.COMMON, title='Type')
    external_number: Optional[str] = Field(default=False, title='External #', table=True)
    store_id: Optional[UUID4] = Field(default=None, title='Store Id')
    company_ids: Optional[list[UUID4]] = Field(default=None, title='Сompanies')
    role_ids: Optional[list[UUID4]] = Field(default=None, title='Roles')


class UserUpdateScheme(UserBaseScheme):
    nickname: Optional[str] = Field(default=None,title='Nickname', table=True, form=True)
    locale: TypeLocale = None
    email: str = None


class UserCreateScheme(UserBaseScheme):
    password1: str = Field(..., description="Password1")
    password2: str = Field(..., description="Password2")
    password: Optional[str] = None
    # password: Optional[str]


class UserScheme(UserBaseScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    phone_number: Optional[TypePhone]
    locale: Optional[TypeLocale]
    country: Optional[TypeCountry]
    company_id: Optional[UUID4]
    company_rel: Optional[CompanyScheme]
    store_rel: Optional[StoreScheme]

    class Config:
        orm_mode = True


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
    user: UserCreateScheme
    company: CompanyCreateScheme


class ChangeCompanyScheme(BaseModel):
    user_id: UUID4
    company_id: UUID4
