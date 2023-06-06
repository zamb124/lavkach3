from pydantic import BaseModel, Field, UUID4
from core.repository.base import BaseRepo
from app.company.models import Company


class CompanyResponseSchema(BaseModel, BaseRepo):
    id: UUID4 = Field(..., description="ID")
    title: str = Field(..., description="Email")
    lang: str = Field(..., description="Nickname")
    country: str = Field(..., description="Nickname")
    currency: str = Field(..., description="Nickname")

    class Config:
        orm_mode = True
        model = Company
