from typing import Any, Dict

from babel import Locale
from pydantic import GetJsonSchemaHandler, model_validator
from pydantic_core import CoreSchema
from sqlalchemy_utils.types.country import Country
from sqlalchemy_utils.types.currency import Currency
from sqlalchemy_utils.types.phone_number import PhoneNumber
from pydantic import BaseModel
from core.schemas.basic_schemes import CountrySchema, LocaleSchema, CurrencySchema, PhoneSchema


class TypeCountry(Country):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, c=None):
        if isinstance(v, str):
            try:
                Country(v)
            except ValueError as ex:
                raise TypeError(str(ex))
            return v
        elif isinstance(v, Country):
            return CountrySchema(**{
                'code': v.code,
                'name': v.name
            })
        raise TypeError("Type sqlalchemy_utils.types.country.Country or String")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> Dict[str, Any]:
        return {
            'type': 'string',
            'properties': {},
            'title': 'TypeCountry',
            'example': 'US'
        }


class TypeLocale(Locale):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, c=None):
        if isinstance(v, str):
            try:
                Locale(v)
            except ValueError as ex:
                raise TypeError(str(ex))
            except Exception as ex:
                raise TypeError(str(ex))
            return v
        elif isinstance(v, Locale):
            return LocaleSchema(**{
                'language': v.language,
                'territory': 'RU',
                'display_name': v.display_name,
                'english_name': v.english_name,
                'language_name': v.language_name

            })
        raise TypeError("Type babel.Locale or String")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> Dict[str, Any]:
        return {
            'type': 'string',
            'properties': {},
            'title': 'TypeLocale',
            'example': 'en_US'
        }


class TypeCurrency(Currency):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, c=None):
        if isinstance(v, str):
            try:
                Currency(v)
            except ValueError as ex:
                raise TypeError(str(ex))
            return v
        elif isinstance(v, Currency):
            return CurrencySchema(**{
                'code': v.code,
                'name': v.name
            })
        raise TypeError("Type sqlalchemy_utils.types.country.Country or String")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> Dict[str, Any]:
        return {
            'type': 'string',
            'properties': {},
            'title': 'TypeCurrency',
            'example': 'SAE'
        }


class TypePhone(PhoneNumber):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, c=None):
        if isinstance(v, str):
            return v
        elif isinstance(v, PhoneNumber):
            return PhoneSchema(**{
                'country_code': v.country_code,
                'country_code_source': v.country_code_source,
                'e164': v.e164,
                'international': v.international,
                'national': v.national,
                'national_number': v.national_number
            })
        raise TypeError("Type sqlalchemy_utils.types.country.Country or String")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> Dict[str, Any]:
        return {
            'type': 'string',
            'properties': {},
            'title': 'TypePhone',
            'example': '449534771093'
        }
