import datetime
import uuid
import operator
from collections import defaultdict
from enum import Enum
from inspect import isclass
from typing import Optional, Any, get_args, get_origin
from copy import deepcopy
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic.fields import Field
from starlette.datastructures import QueryParams
from starlette.requests import Request

from app.bff.bff_config import config
from app.bff.dff_helpers.filters_cleaner import clean_filter
from core.types import TypeLocale, TypePhone, TypeCountry, TypeCurrency
from random import random


def _get_prefix():
    return uuid.uuid4().hex[:10]
class HTMXException(HTTPException):
    ...


async def get_module_by_model(model):
    for k, v in config.services.items():
        if v['schema'].get(model):
            return k

def list_from_str(v: Any)-> list:
    try:
        return list(set(eval(v)))
    except Exception as ex:
        return []

async def get_types(annotation, _class=[]):
    """
        Рекурсивно берем типы в типах
    """
    if isclass(annotation):
        _class.append(annotation)
        return _class
    else:
        annotate = get_args(annotation)
        origin = get_origin(annotate)
        if origin:
            _class.append(origin)
        await get_types(annotate[0], _class)
    return _class


class HtmxField(BaseModel):
    """
        Описание поля
    """
    field_name: str
    type: Optional[str]
    module: str
    model: str
    required: Optional[bool]
    title: Optional[str]
    enums: Optional[list] = []
    widget: Optional[dict]
    val: Any = None
    sort_idx: Optional[int] = 0



class HtmxHeader(BaseModel):
    """"
        Описание строчки
    """
    fields: list[HtmxField]
    prefix: str = f'header:{_get_prefix()}:'
    id: Optional[uuid.UUID] = None
class HtmxFilter(HtmxHeader):
    """"
        Описание строчки
    """
    prefix: str = f'filter:{_get_prefix()}:'



class HtmxCreate(HtmxHeader):
    """"
        Описание строчки
    """
    prefix: str = f'create:{_get_prefix()}:'
    id: Optional[uuid.UUID] = None


class HtmxLine(HtmxHeader):
    """"
        Описание строчки
    """
    id: uuid.UUID
    lsn: int
    vars: Optional[dict] = None
    company_id: Optional[uuid.UUID] = None
    display_title: Optional[str] = None
    selected: Optional[bool] = False
class HtmxSelect(BaseModel):
    field: HtmxField
    lines: list[HtmxLine] = []
    prefix: str

class HtmxTable(BaseModel):
    """
        Описание таблицы
    """
    module: str
    model: str
    cursor: int
    lines: list[HtmxLine] = Field(default=[], description='Строки таблицы')

class HtmxUpdate(BaseModel):
    """"
        Описание строчки
    """
    ...
    line: HtmxLine = Field(default=[], description='Строка')
    prefix: str = f'update:{_get_prefix()}:'

class HtmxView(BaseModel):
    """"
        Описание строчки
    """
    ...
    line: HtmxLine = Field(default=[], description='Строка')
    prefix: str = f'view:{_get_prefix()}:'

class HtmxConstructorSchemas:
    base: BaseModel
    create: BaseModel
    update: BaseModel
    filter: BaseModel


class HtmxConstructor:
    """
        Класс управление собирания таблиц, форм, строчек и тд связанных с HTMX
    """
    services = config.services
    request: Request
    module: str
    model: str
    schemas: HtmxConstructorSchemas = HtmxConstructorSchemas()
    data: Optional[dict] = None
    params: Optional[QueryParams] = None
    param_filter: Optional[str] = None
    table: Optional[HtmxTable] = None
    select: Optional[HtmxSelect] = None
    form: Optional[BaseModel] = None
    header: Optional[HtmxHeader] = None
    filter: Optional[HtmxFilter] = None
    create: Optional[HtmxCreate] = None
    update: Optional[HtmxUpdate] = None
    view: Optional[HtmxView] = None
    exclude: Optional[list] = None
    join_related: Optional[bool] = True  # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []  # Список присоединяемых полей, если пусто, значит все
    sort: Optional[dict] = {}

    def __init__(self,
                 request,
                 module: str,
                 model: str,
                 param_filter: str = None,
                 data: list | dict = None,
                 params: QueryParams | dict = None,
                 exclude: list = None,
                 join_related: bool = True,
                 join_fields: list = None,
                 sort: list = None
                 ):
        self.request = request
        self.module = module
        self.model = model
        self.param_filter = param_filter
        self.exclude = exclude or []
        self.schemas.base = self.services[self.module]['schema'][self.model]['base']
        self.schemas.create = self.services[self.module]['schema'][self.model]['create']
        self.schemas.update = self.services[self.module]['schema'][self.model]['update']
        self.schemas.filter = self.services[self.module]['schema'][self.model]['filter']

        if data: self._check_data(data)
        if params:
            self._check_params(params)
        else:
            self._check_params(request.query_params)
        self.join_related = join_related
        self.join_fields = join_fields or []
        if sort:
            self.sort = {v: i for i, v in enumerate(sort)}
        else:
            config_sort = self.services[self.module]['schema'][self.model].get('sort')
            if config_sort:
                self.sort = {v: i for i, v in enumerate(config_sort)}

    def _check_data(self, data: list | dict = None):
        if isinstance(self.data, list):
            self.data = {'data': data, 'cursor': 0}
        elif isinstance(self.data, dict):
            self.data = data if data.get('cursor') else {'cursor': 0, 'data': [data, ]}
        else:
            self.data = None

    def _check_params(self, params: QueryParams | dict = None):
        if isinstance(params, QueryParams):
            self.params = clean_filter(params, self.param_filter) if self.param_filter else params
        elif isinstance(params, dict):
            self.params = clean_filter(params, self.param_filter) if self.param_filter else QueryParams(params)
        else:
            self.params = None
        return self.params

    async def get_field(self, field_name, schema: BaseModel):
        """
        Для шаблонизатора распознаем тип для удобства HTMX (универсальные компоненты)
        """
        fielinfo = schema.model_fields[field_name]
        module = self.module
        model = self.model
        res = ''
        enums = []
        class_types = await get_types(fielinfo.annotation, [])
        for i, c in enumerate(class_types):
            if i > 0:
                res += '_'
            if field_name == 'order_by':
                res += 'order_by'
                enums = fielinfo.default
            elif field_name.endswith('_by'):
                res += 'model_id'
                model = 'user'
                module = 'basic'
            elif field_name == 'search':
                res += 'search'
            elif issubclass(class_types[0], bool):
                res += 'bool'
            elif issubclass(class_types[0], uuid.UUID) and field_name in (
                    'allowed_location_src_ids', 'exclusive_location_src_ids', 'allowed_location_dest_ids',
                    'exclusive_location_dest_ids', 'allowed_package_ids', 'exclusive_package_ids'):
                res += 'ids'
                model = 'location'
                module = 'inventory'
            elif issubclass(class_types[0], uuid.UUID) and field_name.endswith('_ids'):
                model_name = field_name.replace('_ids', '')
                res += 'ids'
                module = await get_module_by_model(model_name)
                model = model_name
            elif issubclass(class_types[0], TypeLocale) or field_name.startswith('locale'):
                res += 'locale'
                model = 'locale'
            elif issubclass(class_types[0], TypeCurrency) or field_name.startswith('currency'):
                res += 'currency'
                model = 'currency'
            elif issubclass(class_types[0], TypeCountry) or field_name.startswith('country'):
                res += 'country'
                model = 'country'
            elif issubclass(class_types[0], TypePhone) or field_name.startswith('phone'):
                res += 'phone'
                model = 'phone'
            elif issubclass(c, Enum):
                res += 'enum'
                enums = class_types[0]
            elif issubclass(class_types[0], dict):
                res += 'dict'
            elif issubclass(class_types[0], int):
                res += 'number'
            elif issubclass(class_types[0], uuid.UUID) and field_name.endswith('_id'):
                model_name = field_name.replace('_id', '')
                res += 'model_id'
                module = await get_module_by_model(model_name)
                model = model_name
            elif issubclass(class_types[0], uuid.UUID) and field_name.endswith('_id__in'):
                model_name = field_name.replace('_id__in', '')
                res += 'model_id'
                module = await get_module_by_model(model_name)
                model = model_name or model
            elif issubclass(class_types[0], datetime.datetime):
                res += 'datetime'
            elif issubclass(class_types[0], BaseModel) and field_name.endswith('_list_rel'):
                model_name = field_name.replace('_list_rel', '')
                res += 'model_list_rel'
                module = await get_module_by_model(model_name)
                model = model_name
            elif issubclass(class_types[0], BaseModel) and field_name.endswith('_rel'):
                model_name = field_name.replace('_rel', '')
                res += 'model_rel'
                module = await get_module_by_model(model_name)
                model = model_name
            else:
                res += 'str'
        return HtmxField(**{
            'field_name': field_name,
            'type': res,
            'module': module,
            'model': model,
            'required': fielinfo.is_required(),
            'title': fielinfo.title or model,
            'enums': enums,
            'widget': fielinfo.json_schema_extra or {},
            'sort_idx': self.sort.get(field_name, 999)
        })

    async def _get_schema_fields(self, exclude: list = None, schema: BaseModel = None) -> list[HtmxField]:
        """
            base, filte, update, create
            Отдает ту модель, которая нужна или базовую
        """
        if exclude: self.exclude = exclude
        fields = []
        for k, v in schema.model_fields.items():
            if k in self.exclude:
                continue
            fields.append(
                await self.get_field(field_name=k, schema=schema)
            )
        return fields


    async def _get_header(self, schema: BaseModel, exclude: list = None) -> HtmxHeader:
        """
            Метод отдает хидер , те столбцы с типами для HTMX шаблонов
        """
        fields = await self._get_schema_fields(exclude, schema)
        return HtmxHeader(fields=fields)

    async def multiselect(self) -> HtmxSelect:
        """
            Отдает поле для multiselect и + варианты выбора
            Сначала ищем по параметрам, и если есть уже введенные значения, то доискиваем по ним
        """
        request_data = await self.request.json()
        v = max(request_data['search_terms']) if request_data.get('search_terms') else []
        init_values = list_from_str(request_data.get('values'))
        prefix = request_data.get('prefix')
        clean_data = clean_filter(request_data, prefix)
        field_name = clean_data.get('name')
        field_values = clean_data.get(field_name, [])
        if request_data.get('select_in'): # Значит селект уже идет
            current_values = field_values
        else:
            current_values =init_values
        params = QueryParams({'search': v if v else '', 'size': 100})
        field = await self.get_field(field_name, self.schemas.base)
        field_chema = self.services[field.module]['schema'][field.model]['base']
        self.module, self.model = field.module, field.model
        lines, _ = await self._get_data(schema=field_chema, params=params, join_related=False)
        if current_values:
            _ids_value = []
            data_vals = [str(i.id) for i in lines]
            for v in current_values:
                if v not in data_vals:
                    _ids_value.append(v)
            if _ids_value:
                v_qp = ','.join(_ids_value)
                v_params = QueryParams({'id__in': v_qp})
                _lines,_ = await self._get_data(schema=field_chema, params=v_params,  join_related=False)
                lines += _lines
        for line in lines:
            if str(line.id) in current_values:
                line.selected = True
        field.module = request_data['module']       # Возвращяем оригинальный
        field.model = request_data['model']        # Возвращяем оригинальный
        self.select = HtmxSelect(field=field, lines=lines, prefix=prefix)
        return self.select

    async def get_header(self, exclude: list = None, model_id:uuid.UUID = None) -> HtmxHeader:
        """
            Метод отдает хидер , те столбцы с типами для HTMX шаблонов
        """
        fields = await self._get_schema_fields(exclude, self.schemas.base)
        self.header = HtmxHeader(fields=fields, id=model_id)
        return self.header

    async def get_filter(self, exclude: list = None) -> HtmxFilter:
        """
            Метод отдает фильтр , те столбцы с типами для HTMX шаблонов
        """
        fields = await self._get_schema_fields(exclude, self.schemas.filter)
        self.filter = HtmxFilter(fields=fields)
        return self.filter

    async def get_create(self, exclude: list = None, model_id:uuid.UUID = None) -> HtmxCreate:
        """
            Метод отдает создать схему , те столбцы с типами для HTMX шаблонов
        """
        fields = await self._get_schema_fields(exclude, self.schemas.create)
        self.create = HtmxCreate(fields=fields, id=model_id)
        return self.create

    async def get_update(self, model_id: uuid.UUID, exclude: list = None) -> HtmxUpdate:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        self._check_params({'id__in': model_id})
        lines, _ = await self._get_data(schema=self.schemas.update, join_related=False, exclude=exclude)
        assert len(lines) == 1 or 0
        self.update = HtmxUpdate(line=lines[0])
        return self.update

    async def get_view(self, model_id: uuid.UUID, exclude: list = None) -> HtmxView:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        self._check_params({'id__in': model_id})
        lines, _ = await self._get_data(schema=self.schemas.base, join_related=True, exclude=exclude)
        assert len(lines) == 1 or 0
        self.view = HtmxView(line=lines[0])
        return self.view



    async def get_table(self,
                        params: QueryParams | dict = None,
                        exclude: list = None,
                        join_related: str = True,
                        join_field: list = None
                        ) -> HtmxTable:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        self.header = await self._get_header(self.schemas.base, exclude=exclude)
        lines, cursor = await self._get_data(
            schema=self.schemas.base,
            params=params,
            join_related=join_related,
            exclude=exclude,
            join_field=join_field
        )
        self.table = HtmxTable(module=self.module, model=self.model, lines=lines, cursor=cursor)
        await self._sort_columns()
        return self.table

    async def _get_data(
            self,
            schema: BaseModel,
            exclude: list = None,
            params: QueryParams | dict = None,
            filter: str = None,
            data: list | dict = None,
            join_related: bool = True,
            join_field: list = None
    ):
        """
            Метод отдает таблицу для формата HTMX и Jinja
        """
        if exclude: self.exclude = exclude
        if not params:
            params = self.params
        if data: self._check_data(data)
        if filter: self.param_filter = filter
        if data: self._check_data(data)
        if join_related:
            self.join_related = join_related
        if join_field: self.join_fields = join_field or []
        header = await self._get_header(schema, exclude=exclude)

        async with getattr(self.request.scope['env'], self.module) as a:
            self.data = await a.list(params=params, model=self.model)

        if not self.data.get('data'):
            return [], 0
        lines = []
        htmx_line_temp = header.model_dump()
        for row in self.data['data']:
            line_dict = deepcopy(htmx_line_temp)
            for col in line_dict['fields']:
                col['val'] = row[col['field_name']]
                if col['type'] in ('date', 'datetime'):
                    if col['val']:
                        col['val'] = datetime.datetime.fromisoformat(col['val'])
            lines.append(HtmxLine(
                id=row['id'],
                lsn=row['lsn'],
                vars=row.get('vars'),
                display_title=row.get('title'),
                company_id=row.get('company_id'),
                fields=line_dict['fields']
            ))

        ### Если необходимо сджойнить
        if join_related:
            missing_fields = defaultdict(list)
            for line in lines:
                """Достаем все релейтед обьекты у которых модуль отличается"""
                for field in line.fields:
                    if field.module != self.module:
                        #if field.widget.get('table'):  # TODO: может все надо а не ток table
                        if not self.join_fields:
                            missing_fields[field.field_name].append((field.val, field))
                        elif field.field_name in self.join_fields:
                            missing_fields[field.field_name].append((field.val, field))
            for miss_key, miss_value in missing_fields.items():
                _vals, _fields = [i[0] for i in miss_value], [i[1] for i in miss_value]
                async with getattr(self.request.scope['env'], _fields[0].module) as a:
                    miss_value_str = ''
                    _join_lines = {}
                    if isinstance(_vals, list):
                         miss_value_str = ','.join([i for i in _vals if i])
                    if miss_value_str:
                        qp = QueryParams({'id__in': miss_value_str})
                        _data = await a.list(params=qp, model=_fields[0].model)
                        _join_lines = {i['id']: i for i in _data['data']}
                for _val, _field in zip(_vals, _fields):
                    _field.val = _join_lines.get(_val)

                    if _field.field_name.endswith('_by'):
                        _field.field_name = _field.field_name.replace('_by', '_rel')
                        _field.type = 'model_rel'
                    elif _field.field_name.endswith('_id'):
                        _field.field_name = _field.field_name.replace('_id', '_rel')
                        _field.type = 'model_rel'
                    elif _field.field_name.endswith('_ids'):
                        _field.field_name = _field.field_name.replace('_ids', 'list_rel')
                        _field.type = 'model_list_rel'
                    else:
                        raise HTMXException(status_code=500,
                                            detail=f'Wrong field name {_field.field_name} in table model {_field.model}')

            for col in missing_fields.keys():
                if col.endswith('_by'):
                    new_field_name = col.replace('_by', '_rel')
                elif col.endswith('_id'):
                    new_field_name = col.replace('_id', '_rel')
                elif col.endswith('_ids'):
                    new_field_name = col.replace('_ids', '_list_rel')
                else:
                    raise HTMXException(status_code=500,
                                        detail=f'Wrong field name {col} in table model {self.header.model}')
                for _header_col in header.fields:
                    if col == _header_col.field_name:
                        _header_col.field_name = new_field_name
                        _header_col.type = _header_col.type.replace('_id', '_rel')
                        _header_col.type = _header_col.type.replace('_ids', '_list_rel')
        return lines, self.data['cursor']

    async def get_complete(
            self,
            exclude: list = None,
            params: QueryParams | dict = None,
            filter: str = None,
            data: list | dict = None,
            join_related: bool = True,
            join_field: list = None):

        if exclude: self.exclude = exclude
        if params: self._check_params(params)
        if data: self._check_data(data)
        if filter: self.param_filter = filter
        if data: self._check_data(data)
        if join_related: self.join_related = join_related
        if join_field: self.join_fields = join_field or []
        self.header = await self.get_header()
        self.create = await self.get_create()
        self.update = await self.get_update()
        self.table = await self.get_table()
        await self._sort_columns()

    async def _sort_columns(self):
        self.header.fields.sort(key=lambda x: x.sort_idx)
        if self.table:
            for line in self.table.lines:
                line.fields.sort(key=lambda x: x.sort_idx)
        if self.create:
            self.create.fields.sort(key=lambda x: x.sort_idx)
        if self.update:
            self.update.fields.sort(key=lambda x: x.sort_idx)
