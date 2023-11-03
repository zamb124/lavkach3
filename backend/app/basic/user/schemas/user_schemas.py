from datetime import datetime

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List

from app.basic.company.schemas import CompanyCreateScheme
from app.basic.user.models.user_models import UserType, User
from app.basic.store.schemas.store_schemas import StoreScheme
from core.types.types import *
from core.schemas.list_schema import GenericListSchema


class GetUserListResponseSchema(BaseModel):
    id: UUID4 = Field(..., description="ID")
    email: str = Field(..., description="Email")
    nickname: str = Field(..., description="Nickname")
    type: Optional[UserType]
    store: Optional[StoreScheme]

    class Config:
        orm_mode = True


class CreateUserRequestSchema(BaseModel):
    email: str = Field(..., description="Email")
    password1: str = Field(..., description="Password1")
    password2: str = Field(..., description="Password2")
    nickname: str = Field(..., description="Nickname")
    type: Optional[UserType]
    store_id: Optional[UUID4]

    class Config:
        orm_mode = True


class CreateUserResponseSchema(BaseModel):
    email: str = Field(..., description="Email")
    nickname: str = Field(..., description="Nickname")

    class Config:
        orm_mode = True


class LoginResponseSchema(BaseModel):
    nickname: str
    store_id: Optional[UUID4]
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
    user_id: Optional[UUID4]
    companies: Optional[List[UUID4]]
    permissions: Optional[List[str]]
    roles: Optional[List[str]]
    locale: Optional[str]
    country: Optional[str]


from pydantic import BaseModel, Field, UUID4
from core.schemas.timestamps import TimeStampScheme


class UserBaseScheme(BaseModel):
    vars: Optional[dict] = {}
    email: str = Field(description="Email")
    country: Optional[TypeCountry] = None
    locale: TypeLocale
    phone_number: Optional[TypePhone] = None
    nickname: str
    is_admin: Optional[bool] = None
    type: Optional[str] = None
    external_id: Optional[str] = None
    store_id: Optional[UUID4] = None
    companies: Optional[list[UUID4]] = None
    roles: Optional[list[UUID4]] = None


class UserUpdateScheme(UserBaseScheme):
    nickname: Optional[str] = None
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
    store: Optional[StoreScheme]

    class Config:
        orm_mode = True


class UserFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at_lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at_lt: Optional[datetime] = Field(description="less updated", default=None)
    country__in: Optional[List[str]] = Field(alias="country", default=None)
    external_id__in: Optional[List[str]] = Field(alias="external_id", default=None)
    email__in: Optional[List[str]] = Field(alias="email", default=None)
    nickname__in: Optional[List[str]] = Field(alias="nickname", default=None)
    roles__in: Optional[List[str]] = Field(alias="roles", default=None)
    locale__in: Optional[List[str]] = Field(alias="locale", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str] = None

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = User
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["nickname", "email", "external_id"]


class UserListSchema(GenericListSchema):
    data: Optional[List[UserScheme]]


class SignUpScheme(BaseModel):
    user: UserCreateScheme
    company: CompanyCreateScheme
