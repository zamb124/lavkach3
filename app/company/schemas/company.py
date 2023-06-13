import uuid

from pydantic import BaseModel, Field, UUID4
#from core.service.base import BaseRepo
from app.company.models import Company
from typing import Optional
from core.schemas.timestamps import TimeStampScheme


class CompanyBaseScheme(BaseModel):
    title: str = Field(description="Title")
    external_id: str
    lang: str
    country: str
    currency: str

class CompanyUpdateScheme(CompanyBaseScheme):
    pass
class CompanyCreateScheme(CompanyBaseScheme):
    pass
class CompanyScheme(CompanyCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    class Config:
        orm_mode = True
