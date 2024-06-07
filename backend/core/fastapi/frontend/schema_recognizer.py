import asyncio
import datetime
import enum
import logging
import os
import uuid
from collections import defaultdict
from enum import Enum
from inspect import isclass
from types import UnionType
from typing import Optional, Any, get_args, get_origin, Annotated, Union

from fastapi import HTTPException
from fastapi_filter.contrib.sqlalchemy import Filter
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_fragments import render_block, render_block_async
from pydantic import BaseModel
from starlette.datastructures import QueryParams
from starlette.requests import Request

from core.env import Model
from core.schemas import BaseFilter
from core.utils.timeit import timed


def _get_prefix():
    """Генерирует уникальный идетификатор для модельки"""
    return f'A{uuid.uuid4().hex[:10]}'


async def render(obj: BaseModel, block_name: str, path: str = '') -> object:
    """Рендерит шаблон"""
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

path = os.path.dirname(os.path.abspath(__file__))

environment = Environment(
    loader=FileSystemLoader(f"{path}/templates/"),
    autoescape=select_autoescape(("html", "jinja2"))
)

# Классы исключения для подбора типов
passed_classes = [
    Annotated,
    Union,
    UnionType,
]

def get_types(annotation, _class=[]):
    """
        Рекурсивно берем типы из анотации типа
    """
    if isclass(annotation):
        _class.append(annotation)
        return _class
    else:
        origin = get_origin(annotation)
        annotate = get_args(annotation)
        if origin and origin not in passed_classes:
            _class.append(origin)
        get_types(annotate[0], _class)
    return _class

class Field(BaseModel):
    """
        Описание поля
    """
    field_name: str
    type: str
    model: Any
    required: Optional[bool]
    hidden: Optional[bool] = False
    title: Optional[str]
    enums: Optional[Any] = None
    widget: Optional[dict]
    val: Any = None
    sort_idx: int = 0
    prefix: Optional[str] = None
    line: Optional['Line'] = None
    lines: Optional[list['Line']] = []
    description: str
    schema: Any
    filter: Optional[dict] = None
    is_inline: bool = False
    readonly: bool = False
    color_map: Optional[dict] = {}
    color: Optional[Any] = None

    @property
    def identificator(self):
        """
            Отдает уникальный идентификатор для поля
        """
        return f'{self.prefix}--{self.field_name}'

    def render(self, block_name: str, type: str = '', backdrop: list = []):
        type = type or self.type
        if type == 'list_rel' and self.is_inline:
            block_name = 'inline_as_view'
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'fields/{type}.html',
                block_name=block_name,
                field=self,
                backdrop=backdrop
            )
        except Exception as ex:
            print(ex)
            raise
        return rendered_html

    def as_form(self):
        return self.render(block_name='as_form')

    def as_filter(self):
        return self.render(block_name='as_form')

    def as_view(self, backdrop: list = []):
        return self.render(block_name='as_view', backdrop=backdrop)

    def as_table_header(self):
        return self.render(block_name='as_table_header', type='str')

    def as_table(self):
        return self.render(block_name='as_table')

    def as_table_view(self):
        return render_block(
            environment=environment,
            template_name=f'views/table.html',
            block_name='as_view',
            view=self
        )

    def filter_as_string(self):
        filter = ''
        if self.filter:
            filter +='{'
            for k, v in self.filter.items():
                if isinstance(v, Enum):
                    v= v.name
                filter+= f'"{k}":"{v}",'
            filter+= '}'
        return filter

    def as_table_form(self):
        return render_block(
            environment=environment,
            template_name=f'views/table.html',
            block_name='as_form',
            view=self
        )
    @property
    def is_filter(self):
        if issubclass(self.schema, BaseFilter):
            return True

class SchemaType(str, Enum):
    filter = 'filter'
    create  = 'create'
    update  = 'update'
    get     = 'get'

class Line(BaseModel):
    """"
        Описание строчки
    """
    model: Any
    prefix: str
    schema: Any
    actions: dict
    fields: list[Field]
    id: Optional[uuid.UUID] = None
    lsn: Optional[int] = None
    vars: Optional[dict] = None
    company_id: Optional[uuid.UUID] = None
    display_title: Optional[str] = None
    selected: Optional[bool] = False
    is_inline: bool = False
    field_map: dict = {}

    @property
    def identificator(self):
        return f'{self.prefix}--{self.lsn}'
    def __getitem__(self, item:str):
        idx = self.field_map[item]
        return self.fields[idx]

    def render(self, block_name: str, target_id: str | None = None, backdrop: list  = []):
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'views/line.html',
                block_name=block_name,
                line=self,
                target_id=target_id,
                backdrop=backdrop
            )
        except Exception as ex:
            raise
        return rendered_html

    def get_field(self, field_name: str) -> Field | None:
        for field in self.fields:
            if field.field_name == field_name:
                return field
        return None


    def as_button_view(self, backdrop: list = []):
        return self.render('button_view', backdrop=backdrop)

    def as_button_backdrop(self, backdrop: list = []):
        return self.render('button_backdrop', backdrop=backdrop)

    def as_button_update(self, backdrop: list = []):
        return self.render('button_update', backdrop=backdrop)

    def as_button_create(self, backdrop: list = []):
        return self.render('button_create', backdrop=backdrop)

    def as_button_delete(self, target_id: str|None = None, backdrop: list = []):
        return self.render(block_name='button_delete', target_id=target_id, backdrop=backdrop)

    def as_button_actions(self, target_id: str|None = None, backdrop: list = []):
        return self.render(block_name='button_actions', target_id=target_id, backdrop=backdrop)

    def as_form(self):
        return self.render(block_name='as_form')

    def as_create(self):
        return self.render(block_name='as_create')



class ViewCreate(BaseModel):
    """"
        Описание строчки
    """

    model: Any
    prefix: str
    line: Line
    id: Optional[uuid.UUID] = None


class ViewFilter(ViewCreate):
    """"
        Описание строчки
    """
    ...


class ViewUpdate(ViewCreate):
    """"
        Редактирование
    """
    id: uuid.UUID


class ViewGet(ViewCreate):
    """"
        Cоздание
    """
    id: uuid.UUID | None

class ViewAction(ViewCreate):
    """"
        Cоздание
    """
    ids: list[uuid.UUID]
    action: str


class ViewTable(ViewGet):
    """
        Описание таблицы
    """
    cursor: int
    lines: list[Line] = []
    id: Optional[uuid.UUID] | None = None

    @timed
    def render(self, type: str = 'table'):
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'view/{type}.html',
                block_name='as_view',
                view=self
            )
        except Exception as ex:
            raise
        return rendered_html

    def as_table(self):
        return self.render('table')
    def as__kanban(self):
        return self.render('kanban')



def get_model_actions(model:str | Model, adapter):
    from inspect import signature
    if isinstance(model, str):
        model_name = model
    elif isinstance(model, Model):
        model_name = model.name
    else:
        raise HTMXException(status_code=500, detail='Model is not defined')
    actions = {}
    for i in dir(adapter):
        if i.startswith(f'action_{model_name}'):
            func = getattr(adapter, i),
            schema = signature(func[0]).parameters.get('schema')
            actions.update({
                i: {
                    'func': getattr(adapter, i),
                    'doc': func.__doc__,
                    'schema': schema.annotation if schema else None
                }
            })
    return actions

class ClassView:
    """
        Класс управление собирания таблиц, форм, строчек и тд связанных с HTMX
    """
    request: Request
    model: Model
    params: Optional[QueryParams] | dict | None
    actions: dict | None
    table: Optional[ViewTable] = None
    create: Optional[ViewCreate] = None
    update: Optional[ViewUpdate] = None
    filter: Optional[ViewFilter] = None
    view: Optional[ViewGet] = None
    exclude: Optional[list] = [None]
    join_related: Optional[bool] = True  # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []  # Список присоединяемых полей, если пусто, значит все
    sort: Optional[dict] = {}
    prefix: str
    is_inline: bool = False

    @timed
    def __init__(self,
                 request,
                 model: str,
                 prefix: str | None = None,
                 params: QueryParams | dict | None = None,
                 exclude: list = [],
                 join_related: bool = True,
                 join_fields: list | None = None,
                 sort: list | None = None,
                 is_inline: bool = False
                 ):
        self.request = request
        if isinstance(model, Model):
            self.model = model
        else:
            self.model = request.scope['env'][model]
        assert self.model, 'Model is not defined'
        self.actions = get_model_actions(model, self.model.adapter)
        self.env = request.scope['env']
        self.prefix = prefix or _get_prefix()
        self.exclude = exclude or []
        self.is_inline = is_inline
        if params:
            self.params = params
        else:
            self.params = request.query_params
        self.join_related = join_related
        self.join_fields = join_fields or []
        if sort:
            self.sort = {v: i for i, v in enumerate(sort)}
        else:
            config_sort = self.model.sort
            if config_sort:
                self.sort = {v: i for i, v in enumerate(config_sort)}


    def _get_field(self, field_name, schema: BaseModel, **kwargs):
        """
        Для шаблонизатора распознаем тип для удобства HTMX (универсальные компоненты)
        """
        fielinfo = schema.model_fields[field_name]
        prefix = kwargs.get('prefix') or self.prefix
        res = ''
        enums = []
        line = None
        class_types = get_types(fielinfo.annotation, [])
        model = None
        model_name = self.model.name
        if fielinfo.json_schema_extra:
            if fielinfo.json_schema_extra.get('model'):  # type: ignore
                model_name = fielinfo.json_schema_extra.get('model')  # type: ignore
                model = self.env[model_name]
        for i, c in enumerate(class_types):
            if i > 0:
                res += '_'
            if fielinfo == 'id':
                res += 'id'
            elif issubclass(c, enum.Enum):
                res += 'enum'
                enums = c
            elif issubclass(c, BaseModel):
                try:
                    model_name = c.Config.orm_model.__tablename__
                except Exception as ex:
                    model_name = c.Config.__name__.lower()
                res += 'rel'
                model = self.env[model_name]
                submodel = ClassView(request=self.request, model=model.name)
                line = submodel._get_line(schema=c, model=model, prefix=prefix)
                schema = c
            else:
                res += c.__name__.lower()
        if not model and model_name:
            if model_name == self.model.name:
                model = self.model
            elif model_name != self.model.name:
                model = self.env[model_name]
            assert model, f'Model for field {field_name} is not defined'
        return Field(**{
            'field_name': field_name,
            'type': res,
            'model': model,
            'required': fielinfo.is_required(),
            'hidden': fielinfo.json_schema_extra.get('hidden', False) if fielinfo.json_schema_extra else False,
            'title': fielinfo.title or model.name,
            'enums': enums,
            'widget': fielinfo.json_schema_extra or {},
            'color_map': fielinfo.json_schema_extra.get('color_map', {}) if fielinfo.json_schema_extra else {},
            'readonly': fielinfo.json_schema_extra.get('readonly', False) if fielinfo.json_schema_extra else False,
            'filter': fielinfo.json_schema_extra.get('filter', {}) if fielinfo.json_schema_extra else {},
            'sort_idx': self.sort.get(field_name, 999),
            'description': fielinfo.description or field_name,
            'prefix': prefix,
            'line': line,
            'schema': schema,
            'is_inline': self.is_inline,
        })

    @timed
    def _get_schema_fields(self, schema: BaseModel, **kwargs):
        """
            base, filte, update, create
            Отдает ту модель, которая нужна или базовую
        """
        fields = []
        exclude = kwargs.get('exclude') or self.exclude or []
        exclude_add = []
        field_map = {}
        type = kwargs.get('type')
        if issubclass(schema, Filter):
            for f, v in schema.model_fields.items():
                if v.json_schema_extra:
                    if v.json_schema_extra.get('filter') is False:
                        exclude.append(f)
        if type == 'table':
            for f, v in schema.model_fields.items():
                if v.json_schema_extra:
                    if not v.json_schema_extra.get('table'):  # type: ignore
                        exclude_add.append(f)
                else:
                    exclude_add.append(f)
            exclude = set(exclude_add) | set(exclude)
        n = 0
        for k, v in schema.model_fields.items():
            if k in exclude:
                continue
            f = self._get_field(field_name=k, schema=schema, **kwargs)
            field_map.update({k: n})
            fields.append(f)
            n += 1

        return sorted(fields, key=lambda x: x.sort_idx), field_map


    @timed
    def _get_line(self, schema: BaseModel, **kwargs) -> Line:
        prefix = kwargs.get('prefix') or self.prefix
        id = kwargs.get('model_id')
        lsn = kwargs.get('lsn')
        vars = kwargs.get('vars')
        display_title = kwargs.get('display_title')
        company_id = kwargs.get('company_id')
        fields = kwargs.get('fields')
        field_map = kwargs.get('field_map') or {}
        if not fields:
            fields, field_map = self._get_schema_fields(
                schema=schema,
                prefix=prefix,
                exclude=kwargs.get('exclude'),
                type=kwargs.get('type')
            )
        return Line(
            schema=schema,
            model=self.model,
            lsn=lsn,
            vars=vars,
            display_title=display_title,
            company_id=company_id,
            prefix=prefix,
            fields=fields,
            id=id,
            actions=self.actions,
            is_inline=self.is_inline,
            field_map=field_map,
        )

    @timed
    def get_filter(self) -> str:
        """
            Метод отдает фильтр , те столбцы с типами для HTMX шаблонов
        """
        line = self._get_line(schema=self.model.schemas.filter, prefix=f'{self.prefix}--F')
        self.filter = ViewFilter(model=self.model, line=line, prefix=self.prefix)
        return render_block(
            environment=environment, template_name=f'views/filter.html',
            block_name='filter', filter=self.filter
        )

    async def get_create_line(self, model_id: uuid.UUID | None = None, **kwargs) -> str:
        """
            Метод отдает создать схему , те столбцы с типами для HTMX шаблонов
        """
        prefix = self.prefix
        line = self._get_line(schema=self.model.schemas.create, model_id=model_id, prefix=prefix)
        return render_block(
            environment=environment,
            template_name=f'views/line.html',
            block_name='as_form', line=line
        )

    @timed
    async def get_create(self, model_id: uuid.UUID | None = None, **kwargs) -> str:
        """
            Метод отдает создать схему , те столбцы с типами для HTMX шаблонов
        """
        prefix = self.prefix
        line = self._get_line(schema=self.model.schemas.create, model_id=model_id, prefix=f'{self.prefix}--H')
        self.create = ViewCreate(line=line, id=model_id, prefix=prefix, model=self.model)
        return render_block(
            environment=environment,
            template_name=f'views/modal.html',
            block_name='create', view=self.create, backdrop=kwargs.get('backdrop')
        )

    async def get_update(self, model_id: uuid.UUID, **kwargs) -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        kwargs.update({'type': 'update'})
        params = {'id__in': model_id}
        line, lines, _ = await self._get_data(
            params=params,
            schema=self.model.schemas.update,
            join_related=False,
        )
        assert len(lines) == 1 or 0
        self.update = ViewUpdate(model=self.model, line=lines[0], prefix=self.prefix, id=lines[0].id)
        self._sort_columns()
        return render_block(
            environment=environment,
            template_name=f'views/modal.html',
            block_name='update', view=self.update, backdrop=kwargs.get('backdrop')
        )
    async def get_action(self,action:str, ids:list, schema: BaseModel, **kwargs) -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        kwargs.update({'type': 'update'})
        prefix = self.prefix

        data = {k: ids if k == 'ids' else None for k,v in schema.model_fields.items()}
        line, lines, _ = await self._get_data(
            params={},
            data=[data],
            schema=schema,
            prefix='action--0',
            join_related=False,
        )
        view = ViewAction(ids=ids, line=lines[0], prefix='action--0', model=self.model, action=action)
        return render_block(
            environment=environment,
            template_name=f'views/action.html',
            block_name='action', view=view
        )

    async def get_get(self, model_id: uuid.UUID, **kwargs) -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        kwargs.update({'type': 'view'})
        params = {'id__in': model_id}
        line, lines, _ = await self._get_data(
            params=params,
            schema=self.model.schemas.get,
            join_related=True,
        )
        assert len(lines) == 1 or 0
        self.view = ViewGet(
            model=self.model,
            line=lines[0],
            prefix=self.prefix,
            id=lines[0].id
        )
        self._sort_columns()
        return render_block(
            environment=environment,
            template_name=f'views/modal.html',
            block_name='view',
            view=self.view, backdrop=kwargs.get('backdrop')
        )

    async def get_link_view(self, model_id: uuid.UUID, **kwargs) -> str:
        """

        """
        kwargs.update({'type': 'view'})
        params = {'id__in': model_id}
        line, lines, _ = await self._get_data(
            params=params,
            schema=self.model.schemas.get,
            join_related=False,
        )
        assert len(lines) == 1 or 0, f'Model: {self.model.name}, params: {params}'
        self.view = ViewGet(
            model=self.model,
            line=lines[0],
            prefix=self.prefix,
            id=lines[0].id
        )
        return render_block(
            environment=environment,
            template_name=f'views/link.html',
            block_name='view',
            view=self.view, backdrop=kwargs.get('backdrop')
        )

    async def get_delete(self, model_id: uuid.UUID, target_id: str | None = None, **kwargs) -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        params = {'id__in': model_id}
        line, lines, _ = await self._get_data(
            params=params,
            schema=self.model.schemas.get,
            join_related=True, backdrop=kwargs.get('backdrop')
        )
        assert len(lines) == 1 or 0
        self.view = ViewGet(
            model=self.model,
            line=lines[0],
            prefix=self.prefix,
            id=lines[0].id
        )
        return render_block(
            environment=environment,
            template_name=f'views/modal.html',
            block_name='delete',
            view=self.view,
            target_id=target_id
        )

    @timed
    async def _get_table(self, params: QueryParams | dict | None = None, join_related: bool = True,
                        join_field: list | None = None,
                        widget: str = 'as_view', **kwargs) -> ViewTable:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """

        line, lines, cursor = await self._get_data(
            schema=self.model.schemas.get,
            params=params,
            join_related=join_related,
            join_field=join_field,
            type='table'
        )
        self.table = ViewTable(
            prefix=self.prefix, model=self.model, lines=lines,
            cursor=cursor, line=line
        )
        self._sort_columns()
        return self.table

    @timed
    async def get_table(self, params: QueryParams | dict | None = None, join_related: bool = True, join_field: list | None = None,
                        widget: str = 'as_view', **kwargs) -> str:
        """
            Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов
        """
        await self._get_table(params=params, join_related=join_related, join_field=join_field, widget=widget, **kwargs)
        return render_block(
            environment=environment, template_name=f'views/table.html',
            block_name=widget, view=self.table
        )

    @timed
    async def _get_data(
            self,
            schema: BaseModel,
            params: QueryParams | dict | None = None,
            join_related: bool = True,
            join_field: list | None = None,
            data: list|dict|None = None,
            **kwargs
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
        model = kwargs.get('model') or self.model
        prefix = kwargs.get('prefix') or self.prefix
        type = kwargs.get('type')
        cursor = 0
        line = self._get_line(schema=schema, prefix=f'{prefix}--H', type=type)
        if not data:
            async with model.adapter as a:
                resp_data = await a.list(params=params)
                cursor = resp_data['cursor']
                data = resp_data['data']
            logging.info(f"_GET_DATA END REQUEST: {datetime.datetime.now() - time_start}")
        if not data:
            return line, [], 0
        lines = []
        htmx_line_temp = line.model_dump()
        for row_number, row in enumerate(data):
            line_dict = htmx_line_temp.copy()
            line_dict['prefix'] = prefix + (f'--{row.get("lsn")}' if row.get('lsn') else '')
            for col in line_dict['fields']:
                col['prefix'] = line_dict['prefix']
                col['val'] = row[col['field_name']]
                if col['type'] in ('date', 'datetime'):
                    if col['val']:
                        col['val'] = datetime.datetime.fromisoformat(col['val'])
                elif col['type'] == 'id':
                    if not col['val']:
                        col['val'] = []
                elif col['type'] == 'enum' and col['color_map'] and col['val']:
                     color_enum = col['enums'](col['val'])
                     col['color'] = col['color_map'].get(color_enum)
                elif col['type'].endswith('list_rel'):
                    if val_data := col['val']:
                        line_prefix = f'{line_dict["prefix"]}--{col["field_name"]}'
                        submodel = ClassView(request=self.request, model=col['model'], is_inline=True)
                        col['line'], col['lines'], _ = await submodel._get_data(
                            schema=col['schema'], data=val_data, prefix=line_prefix,
                            model=col['model'], join_related=False, type='inline'
                        )

            lines.append(self._get_line(
                schema=line_dict['schema'],
                model=model,
                model_id=row.get('id'),
                lsn=row.get('lsn'),
                vars=row.get('vars'),
                display_title=row.get('title'),
                company_id=row.get('company_id'),
                fields=line_dict['fields'],
                prefix=f"{prefix}--{row.get('lsn')}",
                idx=row_number,
                is_inline=self.is_inline,
                field_map=line_dict['field_map'],
            ))
        logging.info(f"_GET_DATA LINES SERIALIZE: {datetime.datetime.now() - time_start}")
        ### Если необходимо сджойнить
        if join_related:
            missing_fields = defaultdict(list)
            for line in lines:
                """Достаем все релейтед обьекты у которых модуль отличается"""
                for field in line.fields:
                    if field.model.domain != model.domain or self.model.domain == field.field_name.replace('_id', ''):
                        # if field.widget.get('table'):  # TODO: может все надо а не ток table
                        if not self.join_fields:
                            missing_fields[field.field_name].append((field.val, field))
                        elif field.field_name in self.join_fields:
                            missing_fields[field.field_name].append((field.val, field))
            to_serialize = []
            for miss_key, miss_value in missing_fields.items():
                #_data = []
                _vals, _fields = [i[0] for i in miss_value], [i[1] for i in miss_value]
                miss_value_str = ''
                _corutine_data = None
                if isinstance(_vals, list):
                    miss_value_str = ','.join([i for i in _vals if i])
                if miss_value_str:
                    qp = {'id__in': miss_value_str}
                    _corutine_data = asyncio.create_task(_fields[0].model.adapter.list(params=qp))
                    # _join_lines = {i['id']: i for i in _data['data']}
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
                    if _field.type == 'uuid':
                        _field.type = 'rel'
                    elif _field.type == 'list_uuid':
                        _field.type = 'list_rel'
                    else:
                        raise HTMXException(status_code=500,
                                            detail=f'Wrong field name {_field.field_name} in table model {_field.model}')
            logging.info(f"_GET_DATA GET CORUTINE REALEASE: {datetime.datetime.now() - time_start}")
            for col in missing_fields.keys():
                for _header_col in line.fields:
                    if col == _header_col.field_name:
                        _header_col.type = _header_col.type.replace('uuid', 'rel')
                        _header_col.type = _header_col.type.replace('list_uuid', 'list_rel')
        return line, lines, cursor


    def _sort_columns(self):
        if self.table:
            self.table.line.fields.sort(key=lambda x: x.sort_idx)
            for line in self.table.lines:
                line.fields.sort(key=lambda x: x.sort_idx)
        if self.create:
            self.create.line.fields.sort(key=lambda x: x.sort_idx)
        if self.update:
            self.update.line.fields.sort(key=lambda x: x.sort_idx)

        if self.view:
            self.view.line.fields.sort(key=lambda x: x.sort_idx)

    def as_table_widget(self):
        return render_block(
            environment=environment,
            template_name=f'views/table.html',
            block_name='widget',
            cls=self
        )

    def as_filter_widget(self):
        return render_block(
            environment=environment,
            template_name=f'views/filter.html',
            block_name='widget',
            cls=self
        )

    def as_header_widget(self):
        return render_block(
            environment=environment,
            template_name=f'views/header.html',
            block_name='widget',
            cls=self
        )

    def as_button_create(self):
        line = self._get_line(schema=self.model.schemas.create)
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'views/model.html',
                block_name='button_create',
                line=line,
            )
        except Exception as ex:
            raise
        return rendered_html

    def send_message(self, message: str):
        return render_block(
            environment=environment,
            template_name=f'components/message.html',
            block_name='success',
            cls=self,
            message=message
        )
