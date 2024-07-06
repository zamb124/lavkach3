import asyncio
import enum
import os
import uuid
from inspect import isclass
from typing import Optional, get_args, get_origin

from fastapi_filter.contrib.sqlalchemy import Filter
from jinja2_fragments import render_block
from pydantic import BaseModel
from pydantic import Field as PyFild
from pydantic.fields import FieldInfo
from starlette.datastructures import QueryParams
from starlette.requests import Request

from core.env import Model
from core.fastapi.frontend.line import Line, Lines
from core.fastapi.frontend.enviroment import passed_classes, readonly_fields, hidden_fields, table_fields, \
    reserved_fields, environment
from core.fastapi.frontend.field import Field, Fields
from core.fastapi.frontend.types import LineType, ViewVars, MethodType
from core.schemas import BaseFilter
from core.schemas.basic_schemes import ActionBaseSchame
from core.utils.timeit import timed


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


class ClassView(AsyncObj):
    """
        Классконструктор модели для манипулирование уже их UI HTMX
    """
    request: Request  # Реквест - TODO: надо потом убрать
    model_name: str  # Имя поля
    vars: Optional[dict] = None  # Переменные если нужно передать контекст
    model: Model  # Модель данных
    params: Optional[QueryParams] | dict | None  # Параметры на вхрде
    join_related: Optional[bool] = True  # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []  # Список присоединяемых полей, если пусто, значит все
    lines: Lines  # Список обьектов
    action_line: Optional[Line] = None  # Если конструктор выступает в роли Экшена
    action_lines: Optional[Lines] = None  # Если конструктор выступает в роли Экшена
    exclude: Optional[list] = [None]  # Исключаемые солбцы
    sort: Optional[dict] = {}  # Правила сортировки
    key: str  # Ключ конструктора
    actions: False  # Доступные Методы модели
    is_rel: bool = False  # True, если

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
        self.lines = Lines(class_key=self.key, cls=self)
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

    async def get_line_by_id(self, id: uuid.UUID):
        return await self.get_line(id)

    async def get_line_by_fieldinfo(self, fieldinfo: FieldInfo):
        return await self.get_line(fieldinfo.id)

    async def get_line_by_fieldinfo_or_id(self, fieldinfo_or_id: FieldInfo | uuid.UUID):
        if isinstance(fieldinfo_or_id, uuid.UUID):
            return await self.get_line(fieldinfo_or_id)

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
            domain_name=self.model.domain.name,
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
    def as_table_update(self):
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
                block_name='as_get',
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
