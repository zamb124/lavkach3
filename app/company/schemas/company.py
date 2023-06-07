import uuid

from pydantic import BaseModel, Field, UUID4
from core.repository.base import BaseRepo
from app.company.models import Company
from typing import Optional


class CompanySchema(BaseModel, BaseRepo):
    """
    Упрощенный вид схема, когда подходит в целом и для работы и для API
    """
    id: Optional[UUID4] = Field(description="ID", default_factory=uuid.uuid4)
    title: str = Field(..., description="Email")
    external_id: str = Field(..., description="External ID")
    lang: str = Field(..., description="lang")
    country: str = Field(..., description="Country")
    currency: str = Field(..., description="Currency")

    class Config:
        orm_mode = True
        model = Company # Данная штука служит как бы для обращения к ORM
