import asyncio
import copy
import enum
import enum
import uuid
from collections import defaultdict
from datetime import datetime

from inspect import isclass
from typing import Optional, get_args, get_origin, Any
from starlette.exceptions import HTTPException
from fastapi import Query
from fastapi_filter.contrib.sqlalchemy import Filter
from jinja2_fragments import render_block
from pydantic import BaseModel, UUID4, model_validator
from pydantic.fields import FieldInfo, ComputedFieldInfo
from pydantic.v1.schema import schema
from pydantic_core import ValidationError
from starlette.datastructures import QueryParams
from starlette.requests import Request

from app.front.utills import BaseClass
from core.env import Model, Env
from core.frontend.enviroment import passed_classes, readonly_fields, hidden_fields, table_fields, \
    reserved_fields, environment, _crud_filter
from core.frontend.exceptions import HTMXException
from core.frontend.field import Field, Fields
from core.frontend.types import LineType, ViewVars, MethodType
from core.frontend.utils import clean_filter
from core.schemas import BaseFilter
from core.schemas.basic_schemes import ActionBaseSchame, BasicField
from core.utils.timeit import timed


def _get_key() -> str:
    """Генерирует уникальный идетификатор для конструктора модели"""
    return f'A{uuid.uuid4().hex[:10]}'


def get_types(annotation: object, _class: list = []) -> list[object]:
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


class View:
    """
        Класс описывает контекст конструктора модели,
        ВАЖНО!! класс этот шерится между всеми лайнами,
         <поэтому в нем не должно быть никаких данных
    """
    request: Request = None  # Реквест - TODO: надо потом убрать
    model: Model = None  # Имя поля
    vars: Optional[dict] = {
        'button_update': True,
        'button_view': True,
    }  # Переменные если нужно передать контекст
    params: Optional[QueryParams] | dict | None  # Параметры на вхрде
    join_related: Optional[bool] | None = None  # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []  # Список присоединяемых полей, если пусто, значит все
    submodels: dict
    parent_field: Optional['ClassView'] = None  # Родительский класс
    # Список обьектов
    exclude: Optional[list] = [None]  # Исключаемые солбцы
    sort: dict = dict  # Правила сортировки
    key: str = None  # Ключ конструктора
    actions: dict  # Доступные Методы модели
    is_rel: bool = False  # True, если
    env: Env  # Среда выполнения
    schema: BaseModel


class P:
    """
        Класс инкапсулирует все вспомогательные проперти
    """
    cls: 'ClassView'

    @property
    def key(self) -> str:
        """Ключ лайна"""
        key = f'{self.cls.v.key}--{self.cls._id}'
        return key

    @property
    def ui_key(self) -> str:
        """Сгенерировать ключ обьекта для UI"""
        return f'{self.cls.v.model.name}--{self.cls._id}'

    @property
    def lsn(self) -> str:
        """Сгенерировать ключ обьекта для UI"""
        return self.cls._lsn

    @property
    def id(self) -> str:
        """Сгенерировать ключ обьекта для UI"""
        return self.cls._id

    @property
    def model_name(self) -> str:
        return self.cls.v.model.name

    @property
    def domain_name(self):
        return self.cls.v.model.domain.name

    @property
    def actions(self):
        return self.cls.v.actions

    @property
    def class_key(self):
        """Ключ класса"""
        return self.cls.v.key

    @property
    def display_title(self):
        return self.cls.title.val if hasattr(self.cls, 'title') else self.cls._id


class H:
    """
        Класс инкапсулирует все htmx вызовы шаблонов
    """
    cls: 'ClassView'

    @property
    def button_view(self) -> str:
        """Сгенерировать кнопку на просмотр обьекта"""
        return self.cls.render_line('button_view')

    @property
    def button_update(self) -> str:
        """Сгенерировать кнопку на редактирование обьекта"""
        return self.cls.render_line('button_update')

    @property
    def button_create(self) -> str:
        """Сгенерировать кнопку на создание обьекта"""
        return self.cls.render_line('button_create')

    @property
    def button_delete(self) -> str:
        """Сгенерировать кнопку на удаление обьекта"""
        return self.cls.render_line(block_name='button_delete')

    @property
    def button_save(self) -> str:
        """Кнопка сохранения обьекта"""
        return self.cls.render_line(block_name='button_save')

    @property
    def button_actions(self) -> str:
        """Сгенерировать кнопку на меню доступных методов обьекта"""
        return self.cls.render_line(block_name='button_actions')

    @property
    def as_tr_get(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.cls.render_line(block_name='as_tr', method=MethodType.GET)

    @property
    def as_table_header(self) -> str:
        return self.cls.render_line('as_tr_header')  # type: ignore

    @property
    def as_tr_header(self) -> str:
        """Отобразить обьект как строку заголовок таблицы"""
        return self.cls.render_line(block_name='as_tr_header', method=MethodType.GET)

    @property
    def as_tr_placeholder(self) -> str:
        """Отобразить обьект как строку заголовок таблицы"""
        return self.cls.render_line(block_name='as_tr_placeholder', method=MethodType.GET)

    @property
    def as_tr_update(self) -> str:
        """Отобразить обьект как строку таблицы на редактирование"""
        return self.cls.render_line(block_name='as_tr', method=MethodType.UPDATE)

    @property
    def as_tr_create(self) -> str:
        """Отобразить обьект как строку таблицы на создание"""
        return self.cls.render_line(block_name='as_tr', method=MethodType.CREATE)

    @property
    def as_item(self) -> str:
        """Отобразить обьект как айтем с заголовком"""
        return self.cls.render_line(block_name='as_item', method=MethodType.CREATE)

    @property
    def as_div_get(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.cls.render_line(block_name='as_div', method=MethodType.GET)

    @property
    def as_div_update(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.cls.render_line(block_name='as_div', method=MethodType.UPDATE)

    @property
    def as_div_create(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.cls.render_line(block_name='as_div', method=MethodType.CREATE)

    @property
    def as_card(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.cls.render_line(block_name='as_card', method=MethodType.GET)

    @property
    def get_modal_update(self) -> str:
        """Метод отдает модалку на редактирование обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.UPDATE,
            block_name='modal',
            line=self.cls
        )

    @property
    def get_modal_get(self) -> str:
        """Метод отдает модалку на просмотр обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.GET,
            block_name='modal',
            line=self.cls
        )

    @property
    def get_modal_delete(self) -> str:
        """Метод отдает модалку на удаление обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.DELETE,
            block_name='delete',
            line=self.cls,
        )

    @property
    def get_modal_create(self) -> str:
        """Метод отдает модалку на создание нового обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.CREATE,
            block_name='modal',
            line=self.cls,
        )

    @property
    def get_button_view(self) -> str:
        """Сгенерировать кнопку на просмотр обьекта"""
        return self.cls.render_line('button_view')

    @property
    def get_button_update(self) -> str:
        """Сгенерировать кнопку на редактирование обьекта"""
        return self.cls.render('button_update')

    @property
    def get_button_create(self) -> str:
        """Сгенерировать кнопку на создание обьекта"""
        return self.cls.render('button_create')

    @property
    def get_button_delete(self) -> str:
        """Сгенерировать кнопку на удаление обьекта"""
        return self.cls.render(block_name='button_delete')

    @property
    def get_button_save(self) -> str:
        """Кнопка сохранения обьекта"""
        return self.cls.render(block_name='button_save')

    @property
    def get_button_actions(self) -> str:
        """Сгенерировать кнопку на меню доступных методов обьекта"""
        return self.cls.render(block_name='button_actions')

    @property
    def as_filter(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return render_block(
            environment=environment, template_name=f'cls/filter.html',
            block_name='filter', method=MethodType.UPDATE, cls=self.cls
        )

    @property
    def as_table(self) -> str:
        """Метод отдает Таблицу с хидером на просмотр"""
        return render_block(
            environment=environment, template_name=f'cls/table.html',
            block_name='as_table', method=MethodType.GET, cls=self.cls
        )

    @property
    def as_table_update(self) -> str:
        """Метод отдает Таблицу с хидером на редакетирование"""
        return render_block(
            environment=environment, template_name=f'cls/table.html',
            block_name='as_table', method=MethodType.UPDATE, cls=self
        )

    @property
    def as_table_widget(self) -> str:
        """Отдает виджет HTMX для построение таблицы"""
        return render_block(
            environment=environment,
            template_name=f'cls/table.html',
            block_name='widget',
            method=MethodType.GET,
            cls=self.cls
        )

    @property
    def as_card_kanban(self) -> str:
        """Метод отдает Таблицу с хидером на просмотр"""
        return f'<div class="row" id="{self.key}">{self.lines.as_card_kanban}</div>'

    @property
    def as_card_list(self) -> str:
        """Метод отдает Таблицу с хидером на просмотр"""
        return f'<div class="row" id="{self.key}">{self.lines.as_card_list}</div>'

    @property
    def as_filter_widget(self) -> str:
        """Отдает виджет HTMX для построение фильтра"""
        return render_block(
            environment=environment,
            template_name=f'cls/filter.html',
            block_name='widget',
            cls=self.cls
        )

    @property
    def as_header_widget(self) -> str:
        """Отдает виджет HTMX для построения заголовка страницы обьекта"""
        return render_block(
            environment=environment,
            template_name=f'cls/header.html',
            block_name='widget',
            cls=self.cls
        )

    @property
    def get_import(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return render_block(
            environment=environment, template_name=f'cls/import.html',
            block_name='import_get', method=MethodType.GET, cls=self.cls
        )

    @property
    def get_import_errors(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return render_block(
            environment=environment, template_name=f'cls/import.html',
            block_name='import_errors', method=MethodType.GET, cls=self.cls
        )


class ClassView:
    """
        Классконструктор модели для манипулирование уже их UI HTMX
    """
    _id: str | int = None
    _lsn: int | None = None
    _view: View = None
    _lines: list = []
    __state: int = 0
    p: P = None
    h: H = None

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def __iter__(self):
        return self

    def reset_key(self):
        self._view.key = _get_key()

    def copy(self):
        instance = copy.copy(self)
        for k, attr in instance.__dict__.items():
            if isinstance(attr, Field):
                new_attr = attr.copy()
                setattr(instance, k, new_attr)
                # if attr.cls.v.model.name == instance.v.model.name:
                #     '''Если совпадают классы, то назначаем себя родителем, если нет, значит это '
                #      'другая модель и ее не трогаем'''
                new_attr.cls = instance
        instance.p = P()
        instance.p.cls = instance
        instance.h = H()
        instance.h.cls = instance
        return instance

    def __next__(self):
        """Если использовать конструктор как итератор, то он будет возвращать строки"""
        try:
            line = self._lines[self.__state]
            self.__state += 1
            return line
        except IndexError:
            self.__state = 0
            raise StopIteration

    def ___str__(self):
        return f'{self.v.model.name}:{self._id}'

    def __init__(self,
                 request: Request,
                 model: str,
                 params: dict = None,
                 exclude: list = [],
                 join_related: bool = False,
                 join_fields: list | None = None,
                 is_inline: bool = False,
                 key: str | None = None,
                 is_rel: bool = False,
                 vars: dict | None = None,
                 schema: BaseModel = None,
                 permits: list = [],
                 ):
        self.p = P()
        self.p.cls = self
        self.h = H()
        self.h.cls = self
        self._id = id(self)
        self._view = View()
        self._view.request = request
        if vars:
            self._view.vars = vars
        self._view.model = request.scope['env'][model]
        assert self._view.model, 'Model is not defined'
        self._view.model_name = self._view.model.name
        self._view.is_rel = is_rel
        self._view.actions = self._view.model.adapter.get_actions()
        self._view.env = request.scope['env']
        self._view.key = key or _get_key()
        self._view.exclude = exclude or []
        self._view.params = params or {}
        self._view.join_related = join_related
        self._view.join_fields = join_fields or []
        self._view.schema = schema
        self._view.submodels = {}
        config_sort = self._view.model.sort
        if config_sort:
            self._view.sort = {v: i for i, v in enumerate(config_sort)}
        else:
            self.sort = {}
        self._view.is_inline = is_inline
        ##=======--------
        self._lines = []
        self._get_schema_fields(exclude=exclude)

    @property
    def r(self):
        return self.v.request

    async def init(self, params: dict | None = None, join_related: bool = False,
                   data: list | dict = None, schema: BaseModel = None) -> None:
        """Майнинг данных по params"""
        if not params:
            request_data = await self._view.request.json()
            qp = clean_filter(request_data, self._view.key)
            if qp:
                params = {i: v for i, v in qp[0].items() if v}
        if isinstance(data, list):
            data = {i['id']: i for i in data}
        await self.get_data(params=params, data=data)

    def _get_view_vars_by_fieldinfo(self, fielinfo: FieldInfo | None = None) -> ViewVars:
        if not fielinfo:
            return ViewVars(**{
                'required': False,
                'title': None,
                'hidden': False,
                'color_map': {},
                'readonly': True,
                'filter': {},
                'table': False,
                'form': False,
                'description': None,
            })
        return ViewVars(**{
            'required': fielinfo.is_required() if isinstance(fielinfo, FieldInfo) else False,
            'title': fielinfo.title or str(fielinfo),
            'hidden': fielinfo.json_schema_extra.get('hidden',
                                                     False) if fielinfo.json_schema_extra else False,
            # type: ignore
            'color_map': fielinfo.json_schema_extra.get('color_map',
                                                        {}) if fielinfo.json_schema_extra else {},
            # type: ignore
            'readonly': fielinfo.json_schema_extra.get('readonly',
                                                       False) if fielinfo.json_schema_extra else False,
            # type: ignore
            'filter': fielinfo.json_schema_extra.get('filter',
                                                     {}) if fielinfo.json_schema_extra else {},
            # type: ignore
            'table': fielinfo.json_schema_extra.get('table',
                                                    False) if fielinfo.json_schema_extra else False,

            'form': fielinfo.json_schema_extra.get('form',
                                                    False) if fielinfo.json_schema_extra else False,
            # type: ignore
            'description': fielinfo.description,
        })

    def _get_view_vars(self, fieldname: str, is_filter: bool) -> dict[str, ViewVars]:
        """Костыльный метод собирания ViewVars"""
        if fieldname == 'id':
            a = 1
        create_fields = self._view.model.schemas.create.model_fields | self._view.model.schemas.create.model_computed_fields
        update_fields = self._view.model.schemas.update.model_fields | self._view.model.schemas.update.model_computed_fields
        get_fields = self._view.model.schemas.get.model_fields | self._view.model.schemas.get.model_computed_fields
        filter_fields = self._view.model.schemas.filter.model_fields | self._view.model.schemas.filter.model_computed_fields
        create_fieldinfo = create_fields.get(fieldname)
        update_fieldinfo = update_fields.get(fieldname)
        get_fieldinfo = get_fields.get(fieldname)
        filter_fieldinfo = filter_fields.get(fieldname)
        return {
            'create': self._get_view_vars_by_fieldinfo(create_fieldinfo),
            'update': self._get_view_vars_by_fieldinfo(
                update_fieldinfo) if not is_filter else self._get_view_vars_by_fieldinfo(
                filter_fieldinfo),
            'get': self._get_view_vars_by_fieldinfo(get_fieldinfo),
        }

    def _get_field(self, field_name: str, fields_merged: dict) -> Field:
        """
            Преобразование поля из Pydantic(Field) в схему Field для HTMX
        """
        fielinfo: FieldInfo = fields_merged[field_name]
        res: str = ''
        enums: list = []
        model: Model | None = None
        model_name: str = self._view.model.name
        is_filter: bool = True if self._view.model.schemas.filter.model_fields.get(
            field_name) else False  # type: ignore
        submodel: ClassView | None = None
        if not isinstance(fielinfo, ComputedFieldInfo):
            class_types: list = get_types(fielinfo.annotation, [])
        else:
            class_types: list = [str]

        if fielinfo.json_schema_extra:
            if fielinfo.json_schema_extra.get('model'):  # type: ignore
                model_name = fielinfo.json_schema_extra.get('model')  # type: ignore
                model = self._view.env[model_name]
        for i, c in enumerate(class_types):
            if i > 0:
                res += '_'
            if field_name == 'id':
                res += 'id'
                break
            elif issubclass(c, enum.Enum):  # type: ignore
                res += 'enum'
                enums = c  # type: ignore
            elif issubclass(c, BaseModel):  # type: ignore
                try:
                    model_name = c.Config.orm_model.__tablename__  # type: ignore
                except Exception as ex:
                    model_name = c.Config.__name__.lower()  # type: ignore
                res += 'rel'
                model = self._view.env[model_name]
                submodel = ClassView(
                    request=self._view.request,
                    model=model_name,
                    key=self._view.key,
                )
                self._view.submodels.update({field_name: submodel})
            else:
                res += c.__name__.lower()  # type: ignore

        if not model and model_name:
            if model_name == self._view.model.name:
                model = self._view.model
            elif model_name != self._view.model.name:
                model = self._view.env[model_name]
        assert model, f'Model for field {field_name} is not defined'
        field = Field(**{
            **self._get_view_vars(field_name, is_filter),
            'is_filter': is_filter,
            'field_name': field_name,
            'is_reserved': True if field_name in reserved_fields else False,
            'type': res,
            'model_name': model.name,
            'domain_name': model.domain.name,
            'enums': enums,
            'sort_idx': self._view.sort.get(field_name, 999),
            'cls': self,
            'val': submodel
        })
        return field

    def _get_schema_fields(self, exclude: list = []) -> Fields:
        """Переделывает Pydantic схему на Схему для рендеринга в HTMX и Jinja2 - а зачем?"""
        fields: list[tuple[str, Field]] = []
        n = 0
        fields_merged = self._view.model.schemas.get.model_fields | self._view.model.schemas.get.model_computed_fields | self._view.model.schemas.filter.model_fields
        for k, v in fields_merged.items():
            if k in exclude:
                continue
            f = self._get_field(field_name=k, fields_merged=fields_merged)
            fields.append((k, f))
            n += 1
        fields = sorted(fields, key=lambda x: x[1].sort_idx)
        for field_name, field in fields:
            setattr(self, field_name, field)

    async def get_data(self, params: QueryParams | dict | None = None,
                       data: list | dict | None = None, ) -> None:
        """Метод собирает данные для конструктора модели"""

        if not params:
            params = self._view.params
        if not data:
            if not self._view.model.adapter.domain.domain_type == 'INTERNAL':
                async with self._view.model.adapter as a:  # type: ignore
                    resp_data = await a.list(params=params)
                    data = resp_data['data']
            else:
                data_obj = await self.cls.model.service.list(_filter=params)
                data = [i.__dict__ for i in data_obj]
        self._view.data = {i['id']: i for i in data}
        await self.fill_lines(self._view.data, self.v.join_related, self.v.join_fields)

    async def fill_lines(self, data: dict | list, join_related: bool = False,
                         join_fields: list = []):
        if isinstance(data, list):
            data = {i['id']: i for i in data}
        if not data:
            data = {}
        self._view.data = data
        join_fields = join_fields or self._view.join_fields
        for _id, row in data.items():
            line_copied = self.copy() if self._lines else self
            line_copied._id = row.get('id', id(line_copied))
            line_copied._lsn = row.get('lsn')
            for col in line_copied.get_fields():
                val = row.get(col.field_name, None)
                if col.type in ('date', 'datetime'):
                    if isinstance(val, datetime):
                        pass
                    elif isinstance(val, str):
                        val = datetime.fromisoformat(val)
                elif col.type == 'id':
                    if not val:
                        val = []
                elif col.type.endswith('list_rel'):
                    submodel = line_copied.v.submodels[col.field_name].copy()
                    val = await submodel.fill_lines(data=val, join_related=False)
                    submodel.v.key = col.key
                    submodel.v.parent_field = col
                elif col.type.endswith('rel'):
                    submodel = line_copied.v.submodels[col.field_name].copy()
                    submodel._lines = []
                    val = await submodel.fill_lines(data=[val], join_related=False)
                    submodel.v.key = col.key
                    submodel.v.parent_field = col
                col.val = val
            line_copied._lines.append(line_copied)

        if join_related or join_fields:
            missing_fields = defaultdict(list)
            for _line in self.lines:
                """Достаем все релейтед обьекты у которых модуль отличается"""
                assert _line.fields, "Проверяем что все поля есть"
                for field_name, field in _line.fields.get_fields():
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
                    miss_value_str = ','.join([i for i in set(_vals) if i])
                if miss_value_str:
                    qp = {'id__in': miss_value_str}
                    _corutine_data = asyncio.create_task(
                        self.cls.env[_fields[0].model_name].adapter.list(params=qp))
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
                for _field_name, _header_col in self.line_header.fields.get_fields():  # type: ignore
                    if col == _field_name:
                        _header_col.type = _header_col.type.replace('uuid', 'rel')
                        _header_col.type = _header_col.type.replace('list_uuid', 'list_rel')
        return self

    def get_fields(self, display_view: str = None, method: MethodType = MethodType.GET) -> Fields:
        fields = [k for i, k in self.__dict__.items() if isinstance(k, Field)]
        return _crud_filter(fields, method, display_view)

    def render(self, template_name: str, block_name: str,
               method: MethodType = MethodType.GET) -> str:
        """
            Рендер всего
        """
        return render_block(
            environment=environment,
            template_name=template_name,
            block_name=block_name,
            method=method,
            line=self
        )

    def render_line(self, block_name: str, method: MethodType = MethodType.GET) -> str:
        """Рендеринг подразумеваем 1 лайны из шаблога line"""
        return render_block(
            environment=environment,
            template_name='/line/line.html',
            block_name=block_name,
            method=method,
            line=self,
        )

    @property
    def v(self):
        return self._view

    def send_message(self, message: str) -> str:
        """Отправить пользователю сообщение """
        return render_block(
            environment=environment,
            template_name=f'components/message.html',
            block_name='success',
            cls=self.cls,
            message=message
        )

    async def delete_lines(self, ids: list[uuid.UUID]) -> bool:
        """Метод удаления обьектов"""
        for _id in ids:
            await self.v.model.adapter.delete(id=_id)
        return True

    async def get_lines(self, ids: list[uuid.UUID], join_related: bool = False) -> 'ClassView':
        await self.get_data(params={'id__in': ids})
        return self

    async def update_lines(self, data: dict, id: uuid.UUID) -> 'ClassView':
        """Метод обновления обьектов"""
        new_data = []
        for raw_line in data:
            try:
                method_schema_obj = self.v.model.schemas.update(**raw_line)
            except ValidationError as e:
                raise HTTPException(status_code=406, detail=f"Error: {str(e)}")
            _json = method_schema_obj.model_dump(mode='json', exclude_unset=True)
            line = await self.v.model.adapter.update(id=id, json=_json)
            new_data.append(line)
        lines = await self.fill_lines(new_data)
        return self

    async def create_lines(self, data: dict) -> 'ClassView':
        """Метод создания обьектов"""
        new_data = []
        for raw_line in data:
            raw_line.update({'id': uuid.uuid4()})
            try:
                method_schema_obj = self.v.model.schemas.create(**raw_line)
            except ValidationError as e:
                raise HTTPException(status_code=406, detail=f"Error: {str(e)}")
            _json = method_schema_obj.model_dump(mode='json', exclude_unset=True)
            line = await self.v.model.adapter.create(json=_json)
            new_data.append(line)
        await self.fill_lines(new_data)
        return self

    async def get_action(self, action: str, ids: list[uuid.UUID], schema: BaseModel) -> str:
        """Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов"""
        data = {k: ids if k == 'ids' else None for k, v in schema.model_fields.items()}
        self.action_line = await self._get_line(schema=schema, type=LineType.ACTION)
        self.action_lines = Lines(cls=self, class_key=self.key, line_header=self.action_line,
                                  line_new=self.action_line)
        await self.action_lines.get_data(
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



class Method(str, enum.Enum):
    GET: str = 'get'  # Дать запись на чтение
    CREATE: str = 'create'  # Дать запись на создание
    UPDATE: str = 'update'  # Дать запись на изменение
    DELETE: str = 'delete'  # Дать запись на удаление
    UPDATE_SAVE: str = 'save'  # Сохранить изменения
    CREATE_SAVE: str = 'save_create'  # Сохранить новую запись
    DELETE_SAVE: str = 'delete_delete'  # Подтвердить удаление записи


class BaseSchema(BaseModel):
    model: str
    key: str
    method: Method = Method.GET
    search: str = ''
    filter: Any = None
    id__in: str = None
    cursor: int = 0
    id: UUID4 | int = None
    mode: str = 'get'
    action: str = None
    ids: list[str] = []
    schema: Any = None
    commit: Optional[bool] = False

    @model_validator(mode='before')
    def _filter(cls, value):
        """
            Так же убираем все пустые params
        """
        if f := value.get('filter'):
            if isinstance(f, str):
                try:
                    value['filter'] = eval(f)
                except TypeError as ex:
                    raise 'Type Error'
        return value

    class Config:
        extra = 'allow'


async def get_view(request: Request, schema: BaseSchema) -> ClassView:
    body = await request.json() or {}
    return ClassView(
        request=request,
        model=schema.model,
        key=schema.key,
        schema=schema
    )
