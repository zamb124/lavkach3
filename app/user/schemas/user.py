from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional
from app.user.models.user import UserType
from core.repository.base import BaseRepo
from app.user.models.user import User
from app.store.schemas.store import StoreBaseScheme

class GetUserListResponseSchema(BaseModel):
    id: UUID4 = Field(..., description="ID")
    email: str = Field(..., description="Email")
    nickname: str = Field(..., description="Nickname")
    type: Optional[UserType]
    store: Optional[StoreBaseScheme]

    class Config:
        orm_mode = True


class CreateUserRequestSchema(BaseModel,  BaseRepo):
    email: str = Field(..., description="Email")
    password1: str = Field(..., description="Password1")
    password2: str = Field(..., description="Password2")
    password: Optional[str]
    nickname: str = Field(..., description="Nickname")
    type: Optional[UserType]
    store_id: Optional[UUID4]
    class Config:
        orm_mode = True
        model = User # Данная штука служит как бы для обращения к ORM

class CreateUserResponseSchema(BaseModel):
    email: str = Field(..., description="Email")
    nickname: str = Field(..., description="Nickname")
    type: Optional[UserType]
    class Config:
        orm_mode = True


class LoginResponseSchema(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
