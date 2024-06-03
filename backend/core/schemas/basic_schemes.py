from typing import Optional, Any, List

from pydantic import BaseModel, Json, validator

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
    id: str= None
    language: str
    territory: Optional[str|None] = None
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

