from typing import Optional, List

from pydantic import BaseModel, UUID4, Field

from core.schemas.list_schema import GenericListSchema


class CountrySchema(BaseModel):
    lsn: int = 0
    id: str
    name: str
    code: str


class CountryListSchema(GenericListSchema):
    data: Optional[List[CountrySchema]]


class LocaleSchema(BaseModel):
    lsn: int = 0
    id: str = None
    language: str
    territory: Optional[str | None] = None
    display_name: str
    english_name: str
    language_name: str


class LocaleListSchema(GenericListSchema):
    data: Optional[List[LocaleSchema]]


class CurrencySchema(BaseModel):
    lsn: int = 0
    id: str
    name: str
    code: str


class CurrencyListSchema(GenericListSchema):
    data: Optional[List[CurrencySchema]]


class PhoneSchema(BaseModel):
    id: int = 0
    country_code: int
    country_code_source: int
    e164: str
    international: str
    national: str
    national_number: int


class ActionBaseSchame(BaseModel):
    id: Optional[UUID4] = Field(default=None, title='Id', hidden=True)
    ids: Optional[list[UUID4]] = Field(default=[], title='Ids', hidden=True)
    lsn: Optional[int] = Field(default=0, title='Lsn', hidden=True)
    vars: Optional[dict] = Field(default={}, title='Vars', hidden=True)

    class Config:
        extra = 'allow'


class ActionRescposeSchema(BaseModel):
    status: str
    detail: str
