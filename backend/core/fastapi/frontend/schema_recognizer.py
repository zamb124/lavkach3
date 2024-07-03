import asyncio
import datetime
import enum
import os
import uuid
from collections import defaultdict
from enum import Enum
from inspect import isclass
from types import UnionType
from typing import Optional, Any, get_args, get_origin, Annotated, Union, Iterable

from fastapi import HTTPException
from fastapi_filter.contrib.sqlalchemy import Filter
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_fragments import render_block, render_block_async
from pydantic import BaseModel
from pydantic import Field as PyFild
from pydantic.fields import FieldInfo
from starlette.datastructures import QueryParams
from starlette.requests import Request

from core.env import Model, Env
from core.schemas import BaseFilter
from core.schemas.basic_schemes import ActionBaseSchame
from core.utils.timeit import timed

"""


"""

path = os.path.dirname(os.path.abspath(__file__))

environment = Environment(
    loader=FileSystemLoader(f"{path}/templates/"),
    autoescape=select_autoescape(("html", "jinja2"))
)


def _crud_filter(fields: 'Fields', method: 'MethodType', display_view: str = 'table'):
    """
        Jinja2 флильтр, который фильтрует строки для типа отображений
    """
    return [v for k, v in fields.model_extra.items() if getattr(getattr(v, method.value), display_view)]


def table(fields: 'Fields', method: 'MethodType'):
    """
        Фильтр, который смотрит, если поле подходит к методу
    """
    return _crud_filter(fields, method, 'table')


def form(fields: 'Fields', method: 'MethodType'):
    """
        Фильтр, который смотрит, если поле подходит к методу
    """
    return _crud_filter(fields, method, 'form')


environment.filters['table'] = table

# Классы исключения для подбора типов
passed_classes = [
    Annotated,
    Union,
    UnionType,
]

readonly_fields = [
    'id',
    'lsn',
    'created_at',
    'updated_at',
    'company_id'
]
hidden_fields = [
    'lsn',
    'company_id'
]
table_fields = [
    'id',
    'created_at'
]

reserved_fields = [
    # 'id',
    'company_id',
    'created_by',
    'edited_by',
    'created_at',
    'updated_at',
    'vars'
]


class MethodType(str, Enum):
    CREATE = 'create'
    UPDATE = 'update'
    GET = 'get'
    DELETE = 'delete'


class AsyncObj:
    """
            Обертка что бы класс конструктор собирался Асинхронно
    """

    def __init__(self, *args, **kwargs):
        """
        Standard constructor used for arguments pass
        Do not override. Use __ainit__ instead
        """
        self.__storedargs = args, kwargs
        self.async_initialized = False

    async def __ainit__(self, *args, **kwargs):
        """ Async constructor, you should implement this """

    async def __initobj(self):
        """ Crutch used for __await__ after spawning """
        assert not self.async_initialized
        self.async_initialized = True
        await self.__ainit__(*self.__storedargs[0],
                             **self.__storedargs[1])  # pass the parameters to __ainit__ that passed to __init__
        return self

    def __await__(self):
        return self.__initobj().__await__()

    def __init_subclass__(cls, **kwargs):
        assert asyncio.iscoroutinefunction(cls.__ainit__)  # __ainit__ must be async

    @property
    def async_state(self):
        if not self.async_initialized:
            return "[initialization pending]"
        return "[initialization done and successful]"


def _get_key():
    """Генерирует уникальный идетификатор для конструктора модели"""
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
        try:
            get_types(annotate[0], _class)
        except Exception as ex:
            _class.append(annotation)
    return _class


class FieldFields:
    model_name: str  # Имя поля
    vars: Optional[dict] = None  # Переменные если нужно передать контекст


class ViewVars(BaseModel):
    """
        Набор полей для фронтенда, в разных ракурсах update, create, get
    """
    title: Optional[str] = None  # Tittle - Наименования поля для UI
    hidden: bool = False  # Скрыть его ели нет (Если скрыть совсем, то он не попадет дальше в запросы)
    display: bool = True  # display
    readonly: bool = False  # Только на чтение
    required: bool = False  # Обязательно заполнить, актуально для форм
    table: bool = False  # Учавствует ли поле при построении таблицы
    filter: Optional[dict] = None  # Учавствует ли поле, если это фильтр
    description: Optional[str] = None  # Описание поля в UI


class Field(BaseModel, FieldFields):
    """
        Описание поля
        as_form - виджет поля как редактируемого
        as_view - виджет поля как просмотра
        as_table_form - виджет как таблица (доступен только для list_rel) полей
        as_table - виджет как таблица (доступен только для list_rel) полей
    """
    field_name: str  # Системное имя поля
    type: str  # Тип поля (srt, ins, rel, list_rel ... )
    model_name: str  # Наименование модели
    domain_name: str  # Наименование домена модели
    # widget params
    enums: Optional[Any] = None  # Если поле enum, то тут будет список енумов
    val: Any = None  # Значение поля
    sort_idx: int = 0  # Индекс сортировки поля
    line: Optional['Line'] = None  # Обьект, которому принадлежит поле
    lines: Optional['Lines'] = None  # Если поле list_rel, то субобьекты
    color_map: Optional[dict] = {}  # Мапа для цветовой палитры
    color: Optional[Any] = None  # Значение цвета
    is_filter: bool = False  # Является ли поле фильтром
    is_reserved: bool = False  # Призна
    # Views vars
    get: ViewVars
    create: ViewVars
    update: ViewVars

    @property
    def key(self):
        """Отдает уникальный идентификатор для поля"""
        return f'{self.line.key}--{self.field_name}'

    def render(self, block_name: str, type: str = '', backdrop: list = []):
        type = type or self.type
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'field/{type}.html',
                block_name=block_name,
                field=self,
                backdrop=backdrop
            )
        except Exception as ex:
            print(ex)
            raise
        return rendered_html

    @property
    def label(self):
        """
            Отдать Label for шаблон для поля
        """
        return render_block(
            environment=environment,
            template_name=f'field/label.html',
            block_name='label',
            field=self,
        )

    @property
    def as_form(self):
        """
            Отобразить поле с возможностью редактирования
        """
        return self.render(block_name='as_form')

    @property
    def as_view(self):
        """
            Отобразить поле только на чтение
        """
        return self.render(block_name='as_view')

    @property
    def as_table(self):
        """
            Отобразить поле как Таблицу (Если поле является list_rel)
        """
        return render_block(
            environment=environment,
            template_name=f'cls/table.html',
            block_name='as_table',
            method=MethodType.GET,
            cls=self
        )

    @property
    def as_table_form(self):
        """
            Отобразить поле как Таблицу на редактирование (Если поле является list_rel)
        """
        block_name = 'as_table'
        return render_block(
            environment=environment,
            template_name=f'cls/table.html',
            block_name=block_name,
            method=MethodType.UPDATE,
            cls=self
        )

    def filter_as_string(self):
        """
            Костыльная утилита, что бы в js передать фильтр
        """
        filter = ''
        if self.update.filter:
            filter += '{'
            for k, v in self.update.filter.items():
                if isinstance(v, Enum):
                    v = v.name
                filter += f'"{k}":"{v}",'
            filter += '}'
        return filter


class Fields(BaseModel):
    """
        Обертка для удобства, что бы с полями работать как с обьектом
    """

    class Config:
        extra = 'allow'


class LineType(str, Enum):
    """
        Тип Лайна
        FILTER: Лайн, который обозначеет фильр
        HEADER: Лайн. как заголовок обьекта
        LINE: Лайн с данными
        ACTION: Лайн является Экшеном
    """
    FILTER: str = 'filter'
    HEADER: str = 'header'
    LINE: str = 'line'
    NEW: str = 'new'
    ACTION: str = 'action'


class Line(BaseModel):
    """
        Обертка для обьекта
    """
    type: LineType  # Тип поля СМ LineType
    lines: 'Lines'
    model_name: str  # Имя модели
    schema: Any  # Схема обьекта
    actions: dict  # Доступные методы обьекта
    fields: Optional[Fields] = None  # Поля обьекта
    id: Optional[uuid.UUID] = None  # ID обьекта (если есть)
    lsn: Optional[int] = None  # LSN обьекта (если есть)
    vars: Optional[dict] = None  # vars обьекта (если есть)
    company_id: Optional[uuid.UUID] = None  # Компания обьекта (если есть обьект)
    display_title: Optional[str] = None  # Title (Поле title, или Компьют поле)
    is_last: bool = False  # True Если обьект последний в Lines
    class_key: str  # Уникальный ключ конструктора
    is_rel: bool = False  # True если обьек является relation от поля родителя

    @property
    def key(self):
        """
            Проп генерации UI ключа для обьекта
        """
        if self.type == LineType.LINE:
            key = self.id
        elif self.type == LineType.NEW:
            key = id(self)
        else:
            key = self.type.value
        return f'{self.lines.key}--{key}'

    @timed
    def _change_assign_line(self):
        """Присвоение нового обьекта Line'у"""
        for _, field in self.fields:
            field.line = self

    @timed
    def line_copy(self, type=None):
        """Метод копирования лайна"""
        new_line = self.copy(deep=True)
        if type:
            new_line.type = type
        new_line._change_assign_line()
        if type == LineType.NEW:
            new_line.id = uuid.uuid4()
        return new_line

    def render(self, block_name: str, method: MethodType = MethodType.GET, last=False) -> str:
        """
            block_name: имя блока в шаблоне
            edit: Редактируемые ли поля внутри или нет
        """
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'line/line.html',
                block_name=block_name,
                method=method,
                line=self,
                last=last
            )
        except Exception as ex:
            raise
        return rendered_html

    @property
    def button_view(self):
        """Сгенерировать кнопку на просмотр обьекта"""
        return self.render('button_view')

    @property
    def button_update(self):
        """Сгенерировать кнопку на редактирование обьекта"""
        return self.render('button_update')

    @property
    def button_create(self):
        """Сгенерировать кнопку на создание обьекта"""
        return self.render('button_create')

    @property
    def button_delete(self):
        """Сгенерировать кнопку на удаление обьекта"""
        return self.render(block_name='button_delete')

    @property
    def button_actions(self):
        """Сгенерировать кнопку на меню доступных методов обьекта"""
        return self.render(block_name='button_actions')

    @property
    def as_tr_view(self):
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.render(block_name='as_tr', method=MethodType.GET)

    @property
    def as_tr_header(self):
        """Отобразить обьект как строку заголовок таблицы"""
        return self.render(block_name='as_tr_header', method=MethodType.GET)

    @property
    def as_tr_form(self):
        """Отобразить обьект как строку таблицы на редактирование"""
        return self.render(block_name='as_tr', method=MethodType.UPDATE)

    @property
    def as_tr_add(self) -> str:
        """Отобразить обьект как строку таблицы на создание"""
        return self.render(block_name='as_tr', method=MethodType.CREATE)

    @property
    def as_card_form(self):
        """Отобразить обьект как card на редактирование"""
        return self.render(block_name='as_form')

    @property
    def as_card_view(self):
        """Отобразить обьект как card на просмотр"""
        return self.render(block_name='as_form')

    @property
    def get_update(self) -> str:
        """Метод отдает модалку на редактирование обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.UPDATE,
            block_name='modal',
            line=self
        )

    @property
    def get_get(self) -> str:
        """Метод отдает модалку на просмотр обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.GET,
            block_name='modal',
            line=self
        )

    @property
    def get_delete(self) -> str:
        """Метод отдает модалку на удаление обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.DELETE,
            block_name='delete',
            line=self,
        )

    @property
    def get_create(self) -> str:
        """Метод отдает модалку на создание нового обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.CREATE,
            block_name='modal',
            line=self,
        )


class FilterLine(Line):
    ...


class Lines(BaseModel):
    """Делаем класс похожий на List и уже работаем с ним"""
    parent_field: Optional[Any] = None
    class_key: Optional[str]
    line_header: Optional[Line] = None
    line_new: Optional[Line] = None
    line_filter: Optional[Line] = None
    lines: list['Line'] = []
    vars: Optional[dict] = {}

    params: Optional[dict] = {}  # Параметры на вхрде
    join_related: Optional[bool] = True  # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []  # Список присоединяемых полей, если пусто, значит все

    @property
    def key(self):
        return self.parent_field.key if self.parent_field else self.class_key

    def __bool__(self):
        if not self.lines:
            return False
        else:
            return True

    def __deepcopy__(self, memodict={}):
        return self

    @timed
    async def _get_data(
            self,
            env: Env,
            model: Model,
            params: QueryParams | dict | None = None,
            join_related: bool = True,
            join_fields: list | None = None,
            data: list | dict | None = None,
            **kwargs
    ):
        """Метод собирает данные для конструктора модели"""
        if not params:
            params = self.params
        if join_related:
            self.join_related = join_related
        if join_fields:
            self.join_fields = join_fields or []
        if not data:
            async with model.adapter as a:
                resp_data = await a.list(params=params)
                data = resp_data['data']
        await self.fill_lines(data, join_related, join_fields, env)

    @timed
    async def fill_lines(
            self,
            data: Iterable,
            join_related: bool = False,
            join_fields: list = None,
            env: Env = None,
    ):
        if join_related and not env:
            raise HTMXException(status_code=500, detail=f'Impossible join_related without env')
        i = len(data)
        for n, row in enumerate(data):
            line_copied = self.line_header.line_copy(type=LineType.LINE)
            line_copied.id = row['id']
            line_copied.type = LineType.LINE
            line_copied.is_last = True if i - 1 == n else False
            line_copied.display_title = row.get('title')
            line_copied.company_id = row.get('company_id')
            line_copied.id = row.get('id')
            line_copied.lsn = row.get('lsn')
            for _, col in line_copied.fields:
                col.val = row[col.field_name]
                col.line = line_copied
                if col.type in ('date', 'datetime'):
                    if col.val:
                        col.val = datetime.datetime.fromisoformat(col.val)
                elif col.type == 'id':
                    if not col.val:
                        col.val = []
                elif col.type == 'enum' and col.color_map and col.val:
                    color_enum = col.enums(col.val)
                    col.color = col.color_map.get(color_enum)
                elif col.type.endswith('list_rel'):
                    print(f'rel - {col.lines.line_header.model_name}')
                    col.lines.parent_field = col
                    await col.lines.fill_lines(data=col.val, join_related=False)
            self.lines.append(line_copied)

        if join_related:
            missing_fields = defaultdict(list)
            for _line in self.lines:
                """Достаем все релейтед обьекты у которых модуль отличается"""
                for field_name, field in _line.fields:
                    if field.type in ('uuid',):
                        # if field.widget.get('table'):  # TODO: может все надо а не ток table
                        if not join_fields:
                            missing_fields[field.field_name].append((field.val, field))
                        elif field.field_name in join_fields:
                            missing_fields[field.field_name].append((field.val, field))
            to_serialize = []
            for miss_key, miss_value in missing_fields.items():
                # _data = []
                _vals, _fields = [i[0] for i in miss_value], [i[1] for i in miss_value]
                miss_value_str = ''
                _corutine_data = None
                if isinstance(_vals, list):
                    miss_value_str = ','.join([i for i in _vals if i])
                if miss_value_str:
                    qp = {'id__in': miss_value_str}
                    _corutine_data = asyncio.create_task(env[_fields[0].model_name].adapter.list(params=qp))
                to_serialize.append((_vals, _fields, _corutine_data))
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
                        raise HTMXException(
                            status_code=500,
                            detail=f'Wrong field name {_field.field_name} in table model {_field.model}'
                        )
            for col in missing_fields.keys():
                for _field_name, _header_col in self.line_header.fields:
                    if col == _field_name:
                        _header_col.type = _header_col.type.replace('uuid', 'rel')
                        _header_col.type = _header_col.type.replace('list_uuid', 'list_rel')

    @property
    def as_table_form(self):
        """Метод отдает список обьектов как таблицу на редактирование"""
        rendered_html = ''
        for i, line in enumerate(self.lines):
            if i == len(self.lines) - 1:
                line.is_last = True
            rendered_html += line.as_tr_form
        return rendered_html

    @property
    def as_table_view(self):
        """Метод отдает список обьектов как таблицу на просмотр"""
        rendered_html = ''
        for i, line in enumerate(self.lines):
            if i == len(self.lines) - 1:
                line.is_last = True
            rendered_html += line.as_tr_view
        return rendered_html

    @property
    def as_table_header(self):
        return self.line_header.as_tr_header


class ClassView(AsyncObj, FieldFields):
    """
        Классконструктор модели для манипулирование уже их UI HTMX
    """
    request: Request                                # Реквест - TODO: надо потом убрать
    model: Model                                    # Модель данных
    params: Optional[QueryParams] | dict | None     # Параметры на вхрде
    join_related: Optional[bool] = True             # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []                # Список присоединяемых полей, если пусто, значит все
    lines: Lines                                    # Список обьектов
    action_line: Optional[Line] = None              # Если конструктор выступает в роли Экшена
    action_lines: Optional[Lines] = None            # Если конструктор выступает в роли Экшена
    exclude: Optional[list] = [None]                # Исключаемые солбцы
    sort: Optional[dict] = {}                       # Правила сортировки
    key: str                                        # Ключ конструктора
    actions: False                                  # Доступные Методы модели
    is_rel: bool = False                            # True, если

    async def __ainit__(self,
                        request,
                        model: str | Model = None,
                        params: QueryParams | dict | None = None,
                        exclude: list = [],
                        join_related: bool = True,
                        join_fields: list | None = None,
                        sort: list | None = None,
                        force_init: bool = False,
                        is_inline: bool = False,
                        key: str | None = None,
                        is_rel: bool = False
                        ):
        self.request = request
        if isinstance(model, Model):
            self.model = model
        elif model:
            self.model = request.scope['env'][model]
        elif self.model_name:
            self.model = request.scope['env'][self.model_name]
        try:
            assert self.model, 'Model is not defined'
        except Exception as ex:
            raise
        self.model_name = self.model.name
        self.is_rel = is_rel
        self.actions = self.model.adapter.get_actions()
        self.env = request.scope['env']
        self.key = key or _get_key()
        self.exclude = exclude or []
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
        self.is_inline = is_inline
        self.lines = Lines(class_key=self.key)
        line_header = await self._get_line(
            schema=self.model.schemas.get,
            type=LineType.HEADER,
            class_key=self.key,
            view=self
        )
        self.lines.line_header = line_header
        line_new = self.lines.line_header.line_copy(type=LineType.NEW)
        self.lines.line_new = line_new
        line_filter = await self._get_line(
            schema=self.model.schemas.filter,
            type=LineType.FILTER
        )
        self.lines.line_filter = line_filter

        if force_init:
            await self.init()

    async def init(self, params: dict = None, join_related: bool = True):
        """Майнинг данных по params"""

        await self.lines._get_data(
            env=self.env,
            model=self.model,
            schema=self.model.schemas.get,
            params=params or self.params,
            join_related=join_related or self.join_related,
            join_fields=self.join_fields,
        )
        self._sort_columns()

    def _sort_columns(self):
        if self.lines:
            ...
            # sorted(self.line.fields.items(), key=lambda x: x[1].sort_idx)
            for line in self.lines:
                ...  # line.fields.sort(key=lambda x: x.sort_idx)

    def _get_view_vars_by_fieldinfo(self, fielinfo: FieldInfo = None):
        if not fielinfo:
            return ViewVars(**{
                'required': False,
                'title': None,
                'hidden': False,
                'color_map': {},
                'readonly': True,
                'filter': {},
                'table': False,
                'description': None,
            })
        return ViewVars(**{
            'required': fielinfo.is_required(),
            'title': fielinfo.title or str(fielinfo),
            'hidden': fielinfo.json_schema_extra.get('hidden', False) if fielinfo.json_schema_extra else False,
            'color_map': fielinfo.json_schema_extra.get('color_map', {}) if fielinfo.json_schema_extra else {},
            'readonly': fielinfo.json_schema_extra.get('readonly', False) if fielinfo.json_schema_extra else False,
            'filter': fielinfo.json_schema_extra.get('filter', {}) if fielinfo.json_schema_extra else {},
            'table': fielinfo.json_schema_extra.get('table', False) if fielinfo.json_schema_extra else False,
            'description': fielinfo.description,
        })

    def _get_view_vars(self, fieldname: str, is_filter: bool, schema: BaseModel):
        """Костыльный метод собирания ViewVars"""
        if schema and issubclass(schema, ActionBaseSchame):
            default_fieldinfo = schema.model_fields.get(fieldname)
            create_fieldinfo = update_fieldinfo = get_fieldinfo = filter_fieldinfo = default_fieldinfo
        else:
            create_fieldinfo = self.model.schemas.create.model_fields.get(fieldname)
            update_fieldinfo = self.model.schemas.update.model_fields.get(fieldname)
            get_fieldinfo = self.model.schemas.get.model_fields.get(fieldname)
            filter_fieldinfo = self.model.schemas.filter.model_fields.get(fieldname)
        if fieldname in readonly_fields:
            hidden = True if fieldname in hidden_fields else False
            table = True if fieldname in table_fields else False
            if update_fieldinfo:
                update_fieldinfo.title = fieldname.capitalize()
                if update_fieldinfo.json_schema_extra:
                    update_fieldinfo.json_schema_extra.update({
                        'readonly': True,
                        'table': table,
                        'hidden': hidden
                    })
                else:
                    update_fieldinfo.json_schema_extra = {
                        'readonly': True,
                        'table': table,
                        'hidden': hidden
                    }
            else:
                update_fieldinfo = PyFild(title=fieldname.capitalize(), table=table, hidden=hidden, readonly=True)
            if get_fieldinfo:
                get_fieldinfo.title = fieldname.capitalize()
                if get_fieldinfo.json_schema_extra:
                    get_fieldinfo.json_schema_extra.update({
                        'readonly': True,
                        'table': table,
                        'hidden': hidden
                    })
                else:
                    get_fieldinfo.json_schema_extra = {
                        'readonly': True,
                        'table': table,
                        'hidden': hidden
                    }
            else:
                get_fieldinfo = PyFild(title=fieldname.capitalize(), table=table, hidden=hidden, readonly=True)
            if create_fieldinfo:
                create_fieldinfo.title = fieldname.capitalize()
                if create_fieldinfo.json_schema_extra:
                    create_fieldinfo.json_schema_extra.update({
                        'readonly': True,
                        'table': table,
                        'hidden': hidden
                    })
                else:
                    create_fieldinfo.json_schema_extra = {
                        'readonly': True,
                        'table': table,
                        'hidden': hidden
                    }
            else:
                create_fieldinfo = PyFild(title=fieldname.capitalize(), table=table, hidden=hidden, readonly=True)
        return {
            'create': self._get_view_vars_by_fieldinfo(create_fieldinfo),
            'update': self._get_view_vars_by_fieldinfo(
                update_fieldinfo) if not is_filter else self._get_view_vars_by_fieldinfo(filter_fieldinfo),
            'get': self._get_view_vars_by_fieldinfo(get_fieldinfo),
        }

    async def _get_field(self, line: Line, field_name: str, schema: BaseModel, **kwargs):
        """
            Преобразование поля из Pydantic(Field) в схему Field для HTMX
        """
        fielinfo = schema.model_fields[field_name]
        res = ''
        enums = []
        lines = None
        class_types = get_types(fielinfo.annotation, [])
        model = None
        model_name = self.model.name
        is_filter = True if issubclass(schema, BaseFilter) else False
        if fielinfo.json_schema_extra:
            if fielinfo.json_schema_extra.get('model'):  # type: ignore
                model_name = fielinfo.json_schema_extra.get('model')  # type: ignore
                model = self.env[model_name]
        for i, c in enumerate(class_types):
            if i > 0:
                res += '_'
            if field_name == 'id':
                res += 'id'
                break
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
                submodel = await ClassView(
                    request=self.request,
                    model=model_name,
                    key=line.class_key,
                    force_init=False,
                    is_rel=True
                )  #
                lines = submodel.lines
            else:
                res += c.__name__.lower()

        if not model and model_name:
            if model_name == self.model.name:
                model = self.model
            elif model_name != self.model.name:
                model = self.env[model_name]
            assert model, f'Model for field {field_name} is not defined'
        field = Field(**{
            **self._get_view_vars(field_name, is_filter, schema),
            'is_filter': is_filter,
            'field_name': field_name,
            'is_reserved': True if field_name in reserved_fields else False,
            'type': res,
            'model_name': model.name,
            'domain_name': model.domain.name,
            'enums': enums,
            'sort_idx': self.sort.get(field_name, 999),
            'line': line,
            'lines': lines
        })
        return field

    async def _get_schema_fields(self, line, schema: BaseModel, **kwargs):
        """Переделывает Pydantic схему на Схему для рендеринга в HTMX и Jinja2"""
        fields = {}
        field_class = Fields()
        exclude = kwargs.get('exclude') or self.exclude or []
        exclude_add = []
        if issubclass(schema, Filter):
            for f, v in schema.model_fields.items():
                if v.json_schema_extra:
                    if v.json_schema_extra.get('filter') is False:
                        exclude.append(f)
        if type == 'as_table':
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
            f = await self._get_field(line=line, field_name=k, schema=schema, **kwargs)
            fields[k] = f
            n += 1
        fields = sorted(fields.items(), key=lambda x: x[1].sort_idx)
        for field_name, field in fields:
            setattr(field_class, field_name, field)
        return field_class

    async def _get_line(self, schema: BaseModel, type: LineType, lines: Lines = None, **kwargs) -> Line:
        key = kwargs.get('key') or self.key
        id = kwargs.get('model_id')
        lsn = kwargs.get('lsn')
        vars = kwargs.get('vars')
        display_title = kwargs.get('display_title')
        company_id = kwargs.get('company_id')
        fields = kwargs.get('fields')
        line = Line(
            lines=lines or self.lines,
            type=type,
            schema=schema,
            model_name=self.model.name,
            lsn=lsn,
            vars=vars,
            display_title=display_title,
            company_id=company_id,
            fields=fields,
            id=id,
            actions=self.actions,
            class_key=key,
            is_rel=self.is_rel
        )
        if not fields:
            fields = await self._get_schema_fields(
                line,
                schema=schema,
                exclude=kwargs.get('exclude'),
                type=kwargs.get('type')
            )
        line.fields = fields
        return line

    @property
    def as_filter(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return render_block(
            environment=environment, template_name=f'cls/filter.html',
            block_name='filter', method=MethodType.UPDATE, view=self
        )

    async def get_link_view(self, model_id: uuid.UUID, **kwargs) -> str:
        """ Отдает ссылку на основе ID модели """
        kwargs.update({'type': 'view'})
        params = {'id__in': model_id}
        lines, _ = await self._get_data(
            params=params,
            schema=self.model.schemas.get,
            join_related=False,
        )
        assert len(self.lines.lines) == 1 or 0, f'Model: {self.model.name}, params: {params}'
        return render_block(
            environment=environment,
            template_name=f'cls/link.html',
            block_name='view',
            line=self.lines.lines[0]
        )

    @property
    def as_table(self):
        """Метод отдает Таблицу с хидером на просмотр"""
        return render_block(
            environment=environment, template_name=f'cls/table.html',
            block_name='as_table', method=MethodType.GET, cls=self
        )

    @property
    def as_table_form(self):
        """Метод отдает Таблицу с хидером на редакетирование"""
        return render_block(
            environment=environment, template_name=f'cls/table.html',
            block_name='as_table', method=MethodType.UPDATE, cls=self
        )

    @property
    def as_table_widget(self):
        """Отдает виджет HTMX для построение таблицы"""
        return render_block(
            environment=environment,
            template_name=f'cls/table.html',
            block_name='widget',
            method=MethodType.GET,
            cls=self
        )

    @property
    def as_filter_widget(self):
        """Отдает виджет HTMX для построение фильтра"""
        return render_block(
            environment=environment,
            template_name=f'cls/filter.html',
            block_name='widget',
            cls=self
        )

    @property
    def as_header_widget(self):
        """Отдает виджет HTMX для построения заголовка страницы обьекта"""
        return render_block(
            environment=environment,
            template_name=f'cls/header.html',
            block_name='widget',
            cls=self
        )

    @property
    def button_create(self):
        """Отдает кнопку для создания нового обьекта"""
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'cls/model.html',
                block_name='button_create',
                line=self.line,
            )
        except Exception as ex:
            raise
        return rendered_html

    def send_message(self, message: str):
        """Отправить пользователю сообщение """
        return render_block(
            environment=environment,
            template_name=f'components/message.html',
            block_name='success',
            cls=self,
            message=message
        )
    def delete_by_key(self, key: str):
        """Отправить пользователю сообщение """
        return render_block(
            environment=environment,
            template_name=f'components/delete_by_key.html',
            block_name='delete_by_key',
            key=key,
        )

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

    def as_kanban(self):
        return self.render('kanban')

    async def get_action(self, action: str, ids: list[uuid.UUID], schema: BaseModel) -> str:
        """Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов"""
        data = {k: ids if k == 'ids' else None for k, v in schema.model_fields.items()}
        self.action_line = await self._get_line(schema=schema, type=LineType.ACTION)
        self.action_lines = Lines(class_key=self.key, line_header=self.action_line, line_new=self.action_line)
        await self.action_lines._get_data(
            self.env,
            self.model,
            params={},
            data=[data],
            key='action--0',
            join_related=False,
        )

        return render_block(
            environment=environment,
            template_name=f'cls/action.html',
            block_name='action', cls=self, action=action
        )
