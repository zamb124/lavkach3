import datetime
import logging
import uuid
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from inspect import isclass
from typing import Optional, Any, get_args, get_origin

from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_fragments import render_block, render_block_async
from profilehooks import profile
from pydantic import BaseModel
from pydantic.fields import Field
from starlette.datastructures import QueryParams
from starlette.requests import Request

from app.bff.bff_config import config
from app.bff.template_spec import templates
from core.fastapi.adapters import BaseAdapter
from core.types import TypeLocale, TypePhone, TypeCountry, TypeCurrency
from core.utils.timeit import timed


class DeleteSchema(BaseModel):
    delete_id: uuid.UUID

def _get_prefix():
    return f'{uuid.uuid4().hex[:10]}_'


async def render(obj: BaseModel, block_name: str, path: str = None) -> object:
    try:
        rendered_html = await render_block_async(
            environment=environment,
            template_name=f'{path}',
            block_name=block_name,
            field=obj
        )
    except Exception as ex:
        raise
    return rendered_html


class HTMXException(HTTPException):
    ...


environment = Environment(
    loader=FileSystemLoader("app/bff/templates/"),
    autoescape=select_autoescape(("html", "jinja2")),
    enable_async=True
)


def get_module_by_model(model):
    for k, v in config.services.items():
        if v['schema'].get(model):
            return k


def list_from_str(v: Any) -> list:
    try:
        return list(set(eval(v)))
    except Exception as ex:
        return []


def get_types(annotation, _class=[]):
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
        get_types(annotate[0], _class)
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
    prefix: Optional[str] = None

    def render(self, block_name: str, type: str = None):
        type = type or self.type
        try:
            rendered_html = render_block(
                environment=templates.env,
                template_name=f'fields/{type}.html',
                block_name=block_name,
                field=self
            )
        except Exception as ex:
            raise
        return rendered_html

    def as_form(self):
        return self.render(block_name='as_form')

    def as_filter(self):
        return  self.render(block_name='as_form')

    def as_view(self):
        return self.render(block_name='as_view')

    def as_table_header(self):
        return self.render(block_name='as_table_header', type='str')

    def as_table(self):
        return self.render(block_name='as_table')



class HtmxLine(BaseModel):
    """"
        Описание строчки
    """
    module: str
    model: str
    prefix: str
    fields: list[HtmxField]
    id: Optional[uuid.UUID] = None
    lsn: Optional[int] = None
    vars: Optional[dict] = None
    company_id: Optional[uuid.UUID] = None
    display_title: Optional[str] = None
    selected: Optional[bool] = False


    def render(self, block_name:str, target_id:str = None):
        try:
            rendered_html = render_block(
                environment=templates.env,
                template_name=f'views/line.html',
                block_name=block_name,
                line=self,
                target_id=target_id
            )
        except Exception as ex:
            raise
        return rendered_html

    def as_button_view(self):
        return self.render('button_view')
    def as_button_update(self):
        return self.render('button_update')
    def as_button_create(self):
        return self.render('button_create')
    def as_button_delete(self, target_id:str = None):
        return self.render(block_name='button_delete', target_id=target_id)

class HtmxCreate(BaseModel):
    """"
        Описание строчки
    """
    module: str
    model: str
    prefix: str
    line: HtmxLine
    id: Optional[uuid.UUID] = None



class HtmxFilter(HtmxCreate):
    """"
        Описание строчки
    """
    ...
class HtmxUpdate(HtmxCreate):
    """"
        Редактирование
    """
    line: HtmxLine
    id: uuid.UUID


class HtmxView(HtmxCreate):
    """"
        Cоздание
    """
    line: HtmxLine
    id: uuid.UUID


class HtmxTable(HtmxView):
    """
        Описание таблицы
    """
    cursor: int
    lines: list[HtmxLine] = Field(default=[], description='Строки таблицы')
    id: Optional[uuid.UUID] = None

    @timed
    def render(self):
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'view/table.html',
                block_name='table',
                field=self
            )
        except Exception as ex:
            raise
        return rendered_html

    def as_table(self):
        return self.render()



class HtmxConstructorSchemas:
    base: BaseModel
    create: BaseModel
    update: BaseModel
    filter: BaseModel
    delete: DeleteSchema


class ModelView:
    """
        Класс управление собирания таблиц, форм, строчек и тд связанных с HTMX
    """
    services = config.services
    request: Request
    module: str
    model: str
    schemas: HtmxConstructorSchemas = HtmxConstructorSchemas()
    adapter: BaseAdapter
    params: Optional[QueryParams]
    table: Optional[HtmxTable] = None
    create: Optional[HtmxCreate] = None
    update: Optional[HtmxUpdate] = None
    filter: Optional[HtmxFilter] = None
    view: Optional[HtmxView] = None
    exclude: Optional[list] = [None]
    join_related: Optional[bool] = True  # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []  # Список присоединяемых полей, если пусто, значит все
    sort: Optional[dict] = {}
    prefix: str

    @timed
    def __init__(self,
                 request,
                 module: str,
                 model: str,
                 prefix: str = None,
                 params: QueryParams | dict = None,
                 exclude: list = None,
                 join_related: bool = True,
                 join_fields: list = None,
                 sort: list = None
                 ):
        self.request = request
        self.module = module
        self.model = model
        self.prefix = prefix or _get_prefix()
        self.exclude = exclude or []
        self.schemas.base = self.services[self.module]['schema'][self.model]['base']
        self.schemas.create = self.services[self.module]['schema'][self.model]['create']
        self.schemas.update = self.services[self.module]['schema'][self.model]['update']
        self.schemas.filter = self.services[self.module]['schema'][self.model]['filter']
        self.schemas.delete = DeleteSchema
        self.adapter = getattr(self.request.scope['env'], self.module)
        if params:
            self.params = params
        else:
            self.params = request.query_params
        self.join_related = join_related
        self.join_fields = join_fields or []
        if sort:
            self.sort = {v: i for i, v in enumerate(sort)}
        else:
            config_sort = self.services[self.module]['schema'][self.model].get('sort')
            if config_sort:
                self.sort = {v: i for i, v in enumerate(config_sort)}

    def _get_field(self, field_name, schema: BaseModel):
        """
        Для шаблонизатора распознаем тип для удобства HTMX (универсальные компоненты)
        """
        fielinfo = schema.model_fields[field_name]
        module = self.module
        model = self.model
        prefix = self.prefix
        res = ''
        enums = []
        class_types = get_types(fielinfo.annotation, [])
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
                module = get_module_by_model(model_name)
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
                module =  get_module_by_model(model_name)
                model = model_name
            elif issubclass(class_types[0], uuid.UUID) and field_name.endswith('_id__in'):
                model_name = field_name.replace('_id__in', '')
                res += 'model_id'
                module =  get_module_by_model(model_name)
                model = model_name or model
            elif issubclass(class_types[0], datetime.datetime):
                res += 'datetime'
            elif issubclass(class_types[0], BaseModel) and field_name.endswith('_list_rel'):
                model_name = field_name.replace('_list_rel', '')
                res += 'model_list_rel'
                module =  get_module_by_model(model_name)
                model = model_name
            elif issubclass(class_types[0], BaseModel) and field_name.endswith('_rel'):
                model_name = field_name.replace('_rel', '')
                res += 'model_rel'
                module =  get_module_by_model(model_name)
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
            'sort_idx': self.sort.get(field_name, 999),
            'prefix': prefix
        })

    @timed
    def _get_schema_fields(self, schema: BaseModel) -> list[HtmxField]:
        """
            base, filte, update, create
            Отдает ту модель, которая нужна или базовую
        """
        fields = []
        for k, v in schema.model_fields.items():
            if k in self.exclude:
                continue
            fields.append(
                self._get_field(field_name=k, schema=schema)
            )
        return fields

    @timed
    def _get_line(self, schema: BaseModel, **kwargs) -> HtmxLine:
        id = kwargs.get('model_id')
        fields = self._get_schema_fields(schema=schema)
        return HtmxLine(module=self.module, model=self.model, prefix=self.prefix, fields=fields, id=id)

    @timed
    def get_filter(self) -> str:
        """
            Метод отдает фильтр , те столбцы с типами для HTMX шаблонов
        """
        line = self._get_line(schema=self.schemas.filter)
        self.filter = HtmxFilter(module=self.module, model=self.model, line=line, prefix=self.prefix)
        return render_block(
            environment=templates.env, template_name=f'views/filter.html',
            block_name='filter', filter=self.filter
        )

    @timed
    async def get_create(self, model_id: uuid.UUID = None, **kwargs) -> str:
        """
            Метод отдает создать схему , те столбцы с типами для HTMX шаблонов
        """
        prefix = self.prefix
        line = self._get_line(schema=self.schemas.create, model_id=model_id)
        self.create = HtmxCreate(line=line, id=model_id, prefix=prefix, module=self.module, model=self.model)
        return render_block(
            environment=templates.env,
            template_name=f'views/modal.html',
            block_name='create', view=self.create
        )

    async def get_update(self, model_id: uuid.UUID, **kwargs) -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        params = {'id__in': model_id}
        lines, _ = await self._get_data(
            params=params,
            schema=self.schemas.update,
            join_related=False,
        )
        assert len(lines) == 1 or 0
        self.update = HtmxUpdate(model=self.model, module=self.module, line=lines[0], prefix=self.prefix, id=lines[0].id)
        return render_block(
            environment=templates.env,
            template_name=f'views/modal.html',
            block_name='update', view=self.update
        )

    async def get_view(self, model_id: uuid.UUID, **kwargs) -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        params = {'id__in': model_id}
        lines, _ = await self._get_data(
            params=params,
            schema=self.schemas.base,
            join_related=True,
        )
        assert len(lines) == 1 or 0
        self.view = HtmxView(
            module=self.module,
            model=self.model,
            line=lines[0],
            prefix=self.prefix,
            id=lines[0].id
        )
        return render_block(
            environment=templates.env,
            template_name=f'views/modal.html',
            block_name='view',
            view=self.view
        )

    async def get_delete(self, model_id: uuid.UUID, target_id: str = None) -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        params = {'id__in': model_id}
        lines, _ = await self._get_data(
            params=params,
            schema=self.schemas.base,
            join_related=True,
        )
        assert len(lines) == 1 or 0
        self.view = HtmxView(
            module=self.module,
            model=self.model,
            line=lines[0],
            prefix=self.prefix,
            id=lines[0].id
        )
        return render_block(
            environment=templates.env,
            template_name=f'views/modal.html',
            block_name='delete',
            view=self.view,
            target_id=target_id
        )

    @timed
    async def get_table(self, params: QueryParams | dict = None, join_related: bool = True, join_field: list = None, widget:str = 'table') -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        line = self._get_line(schema=self.schemas.base)
        lines, cursor = await self._get_data(
            schema=self.schemas.base,
            params=params,
            join_related=join_related,
            join_field=join_field
        )
        self.table = HtmxTable(
            prefix=self.prefix, module=self.module, model=self.model, lines=lines,
            cursor=cursor, line=line
        )
        self._sort_columns()
        return render_block(
            environment=templates.env, template_name=f'views/table.html',
            block_name=widget, table=self.table
        )

    @timed
    async def _get_data(
            self,
            schema: BaseModel,
            params: QueryParams | dict = None,
            join_related: bool = True,
            join_field: list = None
    ):
        """
            Метод отдает таблицу для формата HTMX и Jinja
        """
        time_start = datetime.datetime.now()
        logging.info(f"_GET_DATA START: {time_start}")
        if not params:
            params = self.params
        if join_related:
            self.join_related = join_related
        if join_field:
            self.join_fields = join_field or []
        module = self.module
        model = self.model
        line = self._get_line(schema=schema)

        async with getattr(self.request.scope['env'], module) as a:
            data = await a.list(params=params, model=model)
        logging.info(f"_GET_DATA END REQUEST: {datetime.datetime.now() - time_start}")
        if not data.get('data'):
            return [], 0
        lines = []
        htmx_line_temp = line.model_dump()
        for row in data['data']:
            line_dict = deepcopy(htmx_line_temp)
            for col in line_dict['fields']:
                col['val'] = row[col['field_name']]
                if col['type'] in ('date', 'datetime'):
                    if col['val']:
                        col['val'] = datetime.datetime.fromisoformat(col['val'])
                if col['type'] == 'ids':
                    if not col['val']:
                        col['val'] = []
            lines.append(HtmxLine(
                module=module,
                model=model,
                id=row['id'],
                lsn=row['lsn'],
                vars=row.get('vars'),
                display_title=row.get('title'),
                company_id=row.get('company_id'),
                fields=line_dict['fields'],
                prefix=line_dict['prefix']
            ))
        logging.info(f"_GET_DATA LINES SERIALIZE: {datetime.datetime.now() - time_start}")
        ### Если необходимо сджойнить
        if join_related:
            missing_fields = defaultdict(list)
            for line in lines:
                """Достаем все релейтед обьекты у которых модуль отличается"""
                for field in line.fields:
                    if field.module != module or self.model == field.field_name.replace('_id',''):
                        # if field.widget.get('table'):  # TODO: может все надо а не ток table
                        if not self.join_fields:
                            missing_fields[field.field_name].append((field.val, field))
                        elif field.field_name in self.join_fields:
                            missing_fields[field.field_name].append((field.val, field))
            to_serialize = []
            for miss_key, miss_value in missing_fields.items():
                _data = []
                _vals, _fields = [i[0] for i in miss_value], [i[1] for i in miss_value]
                a = getattr(self.request.scope['env'], _fields[0].module)
                miss_value_str = ''
                _corutine_data = None
                if isinstance(_vals, list):
                    miss_value_str = ','.join([i for i in _vals if i])
                if miss_value_str:
                    qp = {'id__in': miss_value_str}
                    _corutine_data = a.list(params=qp, model=_fields[0].model)
                    #_join_lines = {i['id']: i for i in _data['data']}
                to_serialize.append((_vals, _fields, _corutine_data))
            logging.info(f"_GET_DATA GET CORUTINE CREATED: {datetime.datetime.now() - time_start}")
            for _vals, _fields, _corutine_data in to_serialize:
                _join_lines = {}
                if _corutine_data:
                    _data = await _corutine_data
                    _join_lines = {i['id']: i for i in _data['data']}
                for _val, _field in zip(_vals, _fields):
                    if isinstance(_val, list):
                        _new_vals = []
                        for _v in _val:
                            __val = _join_lines.get(_v)
                            if __val:
                                _new_vals.append(__val)
                        _field.val = _new_vals
                    else:
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
            logging.info(f"_GET_DATA GET CORUTINE REALEASE: {datetime.datetime.now() - time_start}")
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
                for _header_col in line.fields:
                    if col == _header_col.field_name:
                        _header_col.field_name = new_field_name
                        _header_col.type = _header_col.type.replace('_id', '_rel')
                        _header_col.type = _header_col.type.replace('_ids', '_list_rel')
        return lines, data['cursor']

    def get_complete(
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
        self.create = self.get_create()
        self.view = self.get_view()
        # self.update = await self.get_update()
        self.table = self.get_table()
        self._sort_columns()

    def _sort_columns(self):
        if self.table:
            self.table.line.fields.sort(key=lambda x: x.sort_idx)
            for line in self.table.lines:
                line.fields.sort(key=lambda x: x.sort_idx)
        if self.create:
            self.create.fields.sort(key=lambda x: x.sort_idx)
        if self.update:
            self.update.fields.sort(key=lambda x: x.sort_idx)

    def as_table_widget(self):
        return render_block(
            environment=templates.env,
            template_name=f'views/table.html',
            block_name='widget',
            model=self
        )
    def as_filter_widget(self):
        return render_block(
            environment=templates.env,
            template_name=f'views/filter.html',
            block_name='widget',
            model=self
        )

    def as_header_widget(self):
        return render_block(
            environment=templates.env,
            template_name=f'views/header.html',
            block_name='widget',
            model=self
        )
    def as_button_create(self):
        line = self._get_line(schema=self.schemas.create)
        try:
            rendered_html = render_block(
                environment=templates.env,
                template_name=f'views/model.html',
                block_name='button_create',
                line=line,
            )
        except Exception as ex:
            raise
        return rendered_html

    def send_message(self, message:str):
        return render_block(
            environment=templates.env,
            template_name=f'components/message.html',
            block_name='success',
            model=self,
            message=message
        )
