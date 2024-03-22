from pydantic import BaseModel, Field, UUID4
from typing import Optional


class LoginRequest(BaseModel):
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
    company_ids: Optional[list[UUID4]]
    role_ids: Optional[list[str]]
