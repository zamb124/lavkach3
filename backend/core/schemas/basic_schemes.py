import typing
from typing import Optional, List, Any

from pydantic import BaseModel, UUID4, Field, AliasPath, AliasChoices, types
from pydantic.config import JsonDict
from pydantic.fields import _EmptyKwargs, computed_field
from pydantic_core import PydanticUndefined
from enum import Enum
from ..schemas.list_schema import GenericListSchema


class BasicModel(BaseModel):
    """
     Переопределяем для удобства
    """
    def check_condition(self, condition: tuple):
        resolution = False
        if len(condition) != 3:
            raise ValueError('Неверное количество аргументов')
        field1, operator, field2 = condition
        match operator:
            case '==':
                ...
            case '!=':
                fieldinfo = self.model_fields.get(field1)
                if fieldinfo is None:
                    raise ValueError(f'Неверное имя поля {field1}')
                annotation = fieldinfo.annotation
                field = getattr(self, field1)
                if isinstance(field, Enum):
                    normalized_value = annotation(field2.lower())
                else:
                    normalized_value = field2
                if field != normalized_value:
                    resolution = True
            case '!=':
                ...
            case '>':
                ...
            case '>=':
                ...
            case '<':
                ...
            case '<=':
                ...
            case 'in':
                ...
            case 'not in':
                ...
        return resolution

    # def model_post_init(self, __context):
    #     if hasattr(self.Config, 'readonly'):
    #         readonly = self.Config.readonly
    #         if isinstance(readonly, bool):
    #             for field_name, field in self.model_fields.items():
    #                 field.json_schema_extra = {'readonly': True}
    #         elif isinstance(readonly, list):
    #             for condition in readonly:
    #                 resolution = self.check_condition(condition)



    class Config:
        extra = 'allow'
        from_attributes = True

_Unset: Any = PydanticUndefined
def BasicField(
        default: Any = PydanticUndefined,
        *,
        #####
        model: str | None = None,               # Имя модели
        readonly: bool | list = False,          # Только на чтение (всегда) или одно из условий  например
        # [('status','==', 'CONFIRMED')]
        table: bool = False,                    # Показывать в таблице
        ####
        default_factory: typing.Callable[[], Any] | None = _Unset,
        alias: str | None = _Unset,
        alias_priority: int | None = _Unset,
        validation_alias: str | AliasPath | AliasChoices | None = _Unset,
        serialization_alias: str | None = _Unset,
        title: str | None = _Unset,
        description: str | None = _Unset,
        examples: list[Any] | None = _Unset,
        exclude: bool | None = _Unset,
        discriminator: str | types.Discriminator | None = _Unset,
        json_schema_extra: JsonDict | typing.Callable[[JsonDict], None] | None = _Unset,
        frozen: bool | None = _Unset,
        validate_default: bool | None = _Unset,
        repr: bool = _Unset,
        init: bool | None = _Unset,
        init_var: bool | None = _Unset,
        kw_only: bool | None = _Unset,
        pattern: str | None = _Unset,
        strict: bool | None = _Unset,
        gt: float | None = _Unset,
        ge: float | None = _Unset,
        lt: float | None = _Unset,
        le: float | None = _Unset,
        multiple_of: float | None = _Unset,
        allow_inf_nan: bool | None = _Unset,
        max_digits: int | None = _Unset,
        decimal_places: int | None = _Unset,
        min_length: int | None = _Unset,
        max_length: int | None = _Unset,
        union_mode: typing.Literal['smart', 'left_to_right'] = _Unset,
        **extra: typing.Unpack[_EmptyKwargs],
):
    """
    Переопределяем для удобства
    """
    return Field(
        default,
        table=table,
        model=model,
        readonly=readonly,
        default_factory= default_factory,
        alias= alias,
        alias_priority= alias_priority,
        validation_alias= validation_alias,
        serialization_alias= serialization_alias,
        title=title  ,
        description=description,
        examples= examples,
        exclude= exclude,
        discriminator=  discriminator,
        json_schema_extra= json_schema_extra,
        frozen= frozen,
        validate_default= validate_default,
        repr= repr,
        init= init,
        init_var= init_var,
        kw_only= kw_only,
        pattern= pattern,
        strict= strict,
        gt= gt,
        ge= ge,
        lt= lt,
        le= le,
        multiple_of= multiple_of,
        allow_inf_nan= allow_inf_nan,
        max_digits= max_digits,
        decimal_places= decimal_places,
        min_length= min_length,
        max_length= max_length,
        union_mode= union_mode,
        **extra,
    )


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
