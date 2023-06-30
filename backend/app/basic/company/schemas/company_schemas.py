from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional, List

from core.schemas.timestamps import TimeStampScheme
from core.types.types import TypeCountry, TypeLocale, TypeCurrency
from core.schemas.list_schema import BaseListSchame


class CompanyBaseScheme(BaseModel):
    title: str = Field(description="Title")
    external_id: Optional[str]
    locale: Optional[TypeLocale]
    country: Optional[TypeCountry]
    currency: Optional[TypeCurrency]

    def __acl__(self):
        def __acl__(self):
            return [
                (Allow, Authenticated, "view"),
                (Allow, "role:admin", "edit"),
                (Allow, f"user:{self.owner}", "delete"),
            ]

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


class CompanyListSchema(BaseListSchame):
    data: List[CompanyScheme] = []
