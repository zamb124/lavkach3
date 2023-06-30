from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional, List
from app.basic.user.models.user_models import UserType
from app.basic.store.schemas.store_schemas import StoreScheme
from app.basic.company.schemas import CompanyScheme
from core.types.types import *
from core.types.types import Locale
from core.schemas.list_schema import BaseListSchame


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
    store_id: Optional[UUID4]
    companies: Optional[list[UUID4]]
    roles: Optional[list[UUID4]]

class UserUpdateScheme(UserBaseScheme):
    pass
class UserCreateScheme(UserBaseScheme):
    password1: str = Field(..., description="Password1")
    password2: str = Field(..., description="Password2")
    password: Optional[str]
    #password: Optional[str]
class UserScheme(UserBaseScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    phone_number: Optional[TypePhone]
    locale: Optional[TypeLocale]
    country: Optional[TypeCountry]
    store: Optional[StoreScheme]

    class Config:
        orm_mode = True

class UserListSchema(BaseListSchame):
    data: List[UserScheme] = []