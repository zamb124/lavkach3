from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional
from core.schemas.timestamps import TimeStampScheme
from core.types.types import *


class CompanyBaseScheme(BaseModel):
    title: str = Field(description="Title")
    external_id: str
    locale: Optional[TypeLocale]
    country: Optional[TypeCountry]
    currency: Optional[TypeCurrency]


class CompanyUpdateScheme(CompanyBaseScheme):
    pass


class CompanyCreateScheme(CompanyBaseScheme):
    pass


class CompanyScheme(CompanyCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    country: TypeCountry
    locale: TypeLocale
    currency: TypeCurrency

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
