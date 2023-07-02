from datetime import datetime

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional, List
from app.basic.user.models.user_models import UserType, User
from app.basic.store.schemas.store_schemas import StoreScheme
from app.basic.company.schemas import CompanyScheme
from core.types.types import *
from core.types.types import Locale
from core.schemas.list_schema import BaseListSchame, GenericListSchema


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
    companies: Optional[List[UUID4]]
    permissions: Optional[List[str]]
    roles: Optional[List[str]]
    locale: Optional[TypeLocale]


from pydantic import BaseModel, Field, UUID4
from core.schemas.timestamps import TimeStampScheme


class UserBaseScheme(BaseModel):
    vars: Optional[dict]
    email: str = Field(description="Email")
    country: Optional[TypeCountry]
    locale: Optional[TypeLocale]
    phone_number: Optional[TypePhone]
    nickname: str
    is_admin: Optional[bool]
    type: Optional[str]
    external_id: Optional[str]
    store_id: Optional[UUID4]
    companies: Optional[list[UUID4]]
    roles: Optional[list[UUID4]]


class UserUpdateScheme(UserBaseScheme):
    pass


class UserCreateScheme(UserBaseScheme):
    password1: str = Field(..., description="Password1")
    password2: str = Field(..., description="Password2")
    password: Optional[str]
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
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id")
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created")
    created_at_lt: Optional[datetime] = Field(description="less created")
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated")
    updated_at_lt: Optional[datetime] = Field(description="less updated")
    country__in: Optional[List[str]] = Field(alias="country")
    external_id__in: Optional[List[str]] = Field(alias="external_id")
    email__in: Optional[List[str]] = Field(alias="email")
    nickname__in: Optional[List[str]] = Field(alias="nickname")
    roles__in: Optional[List[str]] = Field(alias="roles")
    locale__in: Optional[List[str]] = Field(alias="locale")
    order_by: Optional[List[str]]
    search: Optional[str]

    class Config:
        allow_population_by_field_name = True

    class Constants(Filter.Constants):
        model = User
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["nickname", "email", "external_id"]


class UserListSchema(GenericListSchema):
    data: Optional[List[UserScheme]]
