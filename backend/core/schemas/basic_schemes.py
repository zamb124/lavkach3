from typing import Optional, Any

from pydantic import BaseModel, Json, validator


class CountrySchema(BaseModel):
    name: str
    code: str


class LocaleSchema(BaseModel):
    language: str
    territory: str
    display_name: str
    english_name: str
    language_name: str


class CurrencySchema(BaseModel):
    name: str
    code: str


class PhoneSchema(BaseModel):
    country_code: int
    country_code_source: int
    e164: str
    international: str
    national: str
    national_number: int
