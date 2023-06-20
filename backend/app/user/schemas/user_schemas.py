from pydantic import BaseModel, Field, UUID4, Json
from pydantic.types import Optional
from app.user.models.user_models import UserType
from app.store.schemas.store_schemas import StoreScheme
from app.company.schemas.company_schemas import CompanyScheme
from core.types.types import *
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
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")


from pydantic import BaseModel, Field, UUID4
from core.schemas.timestamps import TimeStampScheme


class UserBaseScheme(BaseModel):
    company_id: Optional[UUID4]
    vars: Optional[dict]
    email: str = Field(description="Email")
    country: Optional[TypeCountry]
    locale: Optional[TypeLocale]
    phone_number: Optional[TypePhone]
    nickname: str
    is_admin: Optional[bool]
    type: Optional[str]
    store_id: Optional[UUID4]

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
    company: Optional[CompanyScheme]
    class Config:
        orm_mode = True
