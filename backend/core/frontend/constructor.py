import copy
import enum
import logging
import uuid
from datetime import datetime
from functools import lru_cache
from typing import Optional, Any

from jinja2_fragments import render_block
from pydantic import BaseModel
from pydantic.fields import FieldInfo, ComputedFieldInfo
from pydantic_core import ValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request

from core.env import Model, Env
from core.frontend.enviroment import reserved_fields, environment, _crud_filter
from core.frontend.exceptions import HTMXException
from core.frontend.field import Field, Fields
from core.frontend.types import ViewVars, MethodType
from core.frontend.utils import get_types
from core.schemas.basic_schemes import BasicModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_view(service_name):
    components = service_name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


# Во views нужно регистрировать вьюхи  {'имя модели': 'класс'}
views: dict[str, Any] = {

}

default_templates = {
    'as_tr': 'line/as_tr.html',
    'as_div': 'line/as_div.html',
    'as_card': 'line/as_card.html',
    'as_modal': 'line/as_modal.html',
    'as_button': 'line/as_button.html',
    'as_table': 'cls/as_table.html',
    'as_filter': 'cls/as_filter.html',
    'as_header': 'cls/as_header.html',
    'as_import': 'cls/as_import.html',
}


def _get_key() -> str:
    """Генерирует уникальный идетификатор для конструктора модели"""
    return f'A{uuid.uuid4().hex[:10]}'


class View:
    """
        Класс описывает контекст конструктора модели,
        ВАЖНО!! класс этот шерится между всеми лайнами,
         <поэтому в нем не должно быть никаких данных
    """
    request: Request  # Реквест - TODO: надо потом убрать
    model: Model = None  # Имя поля
    params: Optional[dict] = None  # Параметры на вхрде
    parent_field: 'Field'
    join_related: Optional[bool] | None = None  # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []  # Список присоединяемых полей, если пусто, значит все
    submodels: dict
    # Список обьектов
    exclude: Optional[list] = [None]  # Исключаемые солбцы
    sort: dict = {}  # Правила сортировки
    key: str  # Ключ конструктора
    actions: dict  # Доступные Методы модели
    is_rel: bool = False  # True, если
    env: Env  # Среда выполнения
    schema: BaseModel
    create = True
    delete = True
    actions = None
    update = True
    model_name: str
    data: dict = {}


class P:
    """
        Класс инкапсулирует все вспомогательные проперти
    """
    cls: 'ClassView'

    @property
    def key(self) -> str:
        """Ключ лайна"""
        key = f'{self.cls.p.class_key}--{self.cls._id}'
        return key

    @property
    def ui_key(self) -> str:
        """Сгенерировать ключ обьекта для UI"""
        return f'{self.cls.v.model.name}--{self.cls._id}'

    @property
    def lsn(self) -> int | None:
        """Сгенерировать ключ обьекта для UI"""
        return self.cls._lsn

    @property
    def id(self) -> str | int:
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
        if self.cls.v.parent_field:
            if isinstance(self.cls.v.parent_field, Field):
                return self.cls.v.parent_field.key
            elif isinstance(self.cls.v.parent_field, str):
                return self.cls.v.parent_field
        return self.cls.v.key

    @property
    def is_last(self):
        if not self.cls.v.data:
            return True
        elif len(self.cls._lines) == 1:
            return True
        else:
            last_line = self.cls._lines[-1]
            if last_line._id == self.cls._id:
                return True
        return False

    @property
    def display_title(self):
        return self.cls.title.val if hasattr(self.cls, 'title') else self.cls._id


class H:
    """
    Class for creating flexible methods to generate various HTML components like tables, divs, cards, modals, buttons, filters, and actions using templates.

    Attributes:
        cls: Reference to 'ClassView' for rendering.
        templates: Dictionary holding different templates.

    Methods:
        __init__:
            Initializes the H class by copying default templates.

        as_tr:
            Generates a table row as a string using the specified template, block name, method, and excluding defined fields.

        as_tr_get:
            Displays the object as a table row for viewing.

        as_tr_header:
            Displays the object as a table header row.

        as_tr_placeholder:
            Displays the object as a table header row.

        as_tr_update:
            Displays the object as a table row for editing.

        as_tr_create:
            Displays the object as a table row for creating.

        as_div:
            Generates a div as a string using the specified template, block name, method, and excluding defined fields.

        as_div_get:
            Displays the object as a div for viewing.

        as_div_update:
            Displays the object as a div for updating.

        as_div_create:
            Displays the object as a div for creating.

        as_card:
            Generates a card as a string using the specified template, block name, method, and excluding defined fields.

        as_card_get:
            Displays the object as a card for viewing.

        as_modal:
            Generates a modal as a string using the specified template, block name, method, and excluding defined fields.

        as_modal_get:
            Displays the object as a modal for viewing.

        as_modal_update:
            Displays the object as a modal for updating.

        as_modal_delete:
            Displays the object as a modal for deleting.

        as_modal_create:
            Displays the object as a modal for creating.

        as_button:
            Generates a button as a string using the specified template, block name, method, and excluding defined fields.

        as_button_get:
            Generates a button for viewing the object.

        as_button_update:
            Generates a button for editing the object.

        as_button_create:
            Generates a button for creating the object.

        as_button_delete:
            Generates a button for deleting the object.

        as_button_save:
            Generates a button for saving the object.

        as_button_actions:
            Generates a button for showing available actions on the object.

        as_filter:
            Generates a filter as a string using the specified template, block name, method, and excluding defined fields.

        as_filter_widget:
            Returns an HTMX widget to build a filter.

        as_filter_get:
            Returns a filter with columns and types for HTMX templates.

        as_action:
            Generates an action button for the specified action name, block name, and CSS class.

        as_table:
            Generates a table as a string using the specified template, block name, method, and excluding defined fields.

        as_table_widget:
            Returns the table filter with columns and types for HTMX templates.

        as_table_get:
            Returns the table filter with columns and types for HTMX templates.
    """
    cls: 'ClassView'
    templates: dict[str, str]
    key: str

    def __init__(self):
        self.templates = default_templates.copy()

    def as_tr(self, template: str = 'as_tr', block_name: str = 'get', method: MethodType = MethodType.GET,
              exclude: list = []) -> str:
        """Гибкий метод отдачи строки таблицы"""
        self.cls._exclude = exclude or self.cls._exclude
        template = self.templates.get(template, 'line/as_tr.html')
        return self.cls.render_line(template, block_name=block_name, method=method)

    @property
    def as_tr_get(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_tr()

    @property
    def as_tr_header(self) -> str:
        """Отобразить обьект как строку заголовок таблицы"""
        return self.as_tr(block_name='header')

    @property
    def as_tr_placeholder(self) -> str:
        """Отобразить обьект как строку заголовок таблицы"""
        return self.as_tr(block_name='placeholder')

    @property
    def as_tr_update(self) -> str:
        """Отобразить обьект как строку таблицы на редактирование"""
        return self.as_tr(block_name='update', method=MethodType.UPDATE)

    @property
    def as_tr_create(self) -> str:
        """Отобразить обьект как строку таблицы на создание"""
        return self.as_tr(block_name='create', method=MethodType.CREATE)

    def as_div(self, template: str = 'as_div', block_name: str = 'get', method: MethodType = MethodType.GET,
               exclude: list = []) -> str:
        """Гибкий метод отдачи строки таблицы"""
        self.cls._exclude = exclude or self.cls._exclude
        template = self.templates.get(template, 'line/as_div.html')
        return self.cls.render_line(template, block_name=block_name, method=method)

    @property
    def as_div_get(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_div()

    @property
    def as_div_update(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_div(block_name='update', method=MethodType.UPDATE)

    @property
    def as_div_create(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_div(block_name='create', method=MethodType.CREATE)

    def as_card(self, template: str = 'as_card', block_name: str = 'get', method: MethodType = MethodType.GET,
                exclude: list = []) -> str:
        """Гибкий метод отдачи строки таблицы"""
        self.cls._exclude = exclude or self.cls._exclude
        template = self.templates.get(template, 'line/as_card.html')
        return self.cls.render_line(template, block_name=block_name, method=method)

    @property
    def as_card_get(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_card()

    def as_modal(self, template: str = 'as_modal', block_name: str = 'get', method: MethodType = MethodType.GET,
                 exclude: list = []) -> str:
        """Гибкий метод отдачи строки таблицы"""
        self.cls._exclude = exclude or self.cls._exclude
        template = self.templates.get(template, 'line/as_modal.html')
        return self.cls.render_line(template, block_name=block_name, method=method)

    @property
    def as_modal_get(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_modal()

    @property
    def as_modal_update(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_modal(block_name='update', method=MethodType.UPDATE)

    @property
    def as_modal_delete(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_modal(block_name='delete', method=MethodType.DELETE)

    @property
    def as_modal_create(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.as_modal(block_name='create', method=MethodType.CREATE)

    def as_button(self, template: str = 'as_button', block_name: str = 'get', method: MethodType = MethodType.GET,
                  exclude: list = []) -> str:
        """Гибкий метод отдачи строки таблицы"""
        self.cls._exclude = exclude or self.cls._exclude
        template = self.templates.get(template, 'line/as_button.html')
        return self.cls.render_line(template, block_name=block_name, method=method)

    @property
    def as_button_get(self) -> str:
        """Сгенерировать кнопку на просмотр обьекта"""
        return self.as_button(block_name='get')

    @property
    def as_button_update(self) -> str:
        """Сгенерировать кнопку на редактирование обьекта"""
        return self.as_button(block_name='update')

    @property
    def as_button_create(self) -> str:
        """Сгенерировать кнопку на создание обьекта"""
        return self.as_button(block_name='create')

    @property
    def as_button_delete(self) -> str:
        """Сгенерировать кнопку на удаление обьекта"""
        return self.as_button(block_name='delete')

    @property
    def as_button_save(self) -> str:
        """Кнопка сохранения обьекта"""
        return self.as_button(block_name='save')

    @property
    def as_button_actions(self) -> str:
        """Сгенерировать кнопку на меню доступных методов обьекта"""
        return self.as_button(block_name='actions')

    def as_filter(self, template: str = 'as_filter', block_name: str = 'get', method: MethodType = MethodType.GET,
                  exclude: list = []) -> str:
        """Гибкий метод отдачи строки таблицы"""
        self.cls._exclude = exclude or self.cls._exclude
        template = self.templates.get(template, 'cls/as_filter.html')
        return self.cls.render_line(template, block_name=block_name, method=method)

    @property
    def as_filter_widget(self) -> str:
        """
        Returns the filter widget as an HTML block

          @property
          def as_filter_widget(self) -> str:
              Creates an HTML representation of the filter widget by invoking
              the `as_filter` method with 'widget' as the block name.

          Returns:
              str: The HTML string for the filter widget
        """
        return self.as_filter(block_name='widget')

    @property
    def as_filter_get(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return self.as_filter()

    def as_action(self, action_name, block_name: str = 'button', label=True, css_class=False,
                  icon: Optional[str] = None) -> str:
        """Отдаем кнопку действия"""
        if css_class is True:
            css_class = 'btn btn-primary'
        action = self.cls.v.actions[action_name]
        return render_block(
            environment=environment,
            template_name=f'cls/action.html',
            block_name=block_name,
            action=action,
            line=self.cls,
            label=label,
            css_class=css_class,
            icon=icon or 'solar:double-alt-arrow-right-bold-duotone',
        )

    def as_table(self, template: str = 'as_table', block_name: str = 'get', method: MethodType = MethodType.GET,
                 exclude: list = []) -> str:
        """Гибкий метод отдачи строки таблицы"""
        self.cls._exclude = exclude or self.cls._exclude
        template = self.templates.get(template, 'cls/as_table.html')
        return self.cls.render_line(template, block_name=block_name, method=method)

    @property
    def as_table_widget(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return self.as_table(block_name='widget')

    @property
    def as_table_get(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return self.as_table()

    @property
    def as_table_update(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return self.as_table(method=MethodType.UPDATE)

    @property
    def as_header_widget(self) -> str:
        """Отдает виджет HTMX для построения заголовка страницы обьекта"""
        return render_block(
            environment=environment,
            template_name=f'cls/as_header.html',
            block_name='widget',
            line=self.cls
        )

    @property
    def as_import(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return render_block(
            environment=environment, template_name=f'cls/as_import.html',
            block_name='get', method=MethodType.GET, line=self.cls
        )

    @property
    def as_import_errors(self) -> str:
        """Метод отдает фильтр , те столбцы с типами для HTMX шаблонов"""
        return render_block(
            environment=environment, template_name=f'cls/as_import.html',
            block_name='errors', method=MethodType.GET, line=self.cls
        )


class ClassView:
    """
     class ClassView:
        Represents a view class for handling model-related data and operations.

     _id:
        Unique identifier for the class instance.

     _lsn:
        Optional logging sequence number.

     _view:
        An instance of the View class.

     _exclude:
        List of fields to exclude from operations.

     _lines:
        List storing instances related to the view.

     __state:
        Iterator state for internal use.

     _templates:
        Dictionary mapping template names to paths.

     p:
        Instance of class P.

     h:
        Instance of class H.

     __init__(self, request: Request, model: str | BaseModel, params: dict = None, exclude: list = [],
              join_related: bool = False, join_fields: list | None = None, is_inline: bool = False,
              key: str | None = None, is_rel: bool = False, vars: dict | None = None,
              schema: BaseModel = None, permits: list = [], parent_field: 'Field' = None):
        Initializes an instance of ClassView with the given parameters and model.

     __setattr__(self, key, value):
        Overrides the default behavior for setting attributes.

     __hash__(self):
        Returns the hash value of the _id attribute.

     __eq__(self, other):
        Checks if another instance is equal to this one by comparing their _id attributes.

     __iter__(self):
        Returns the instance itself as an iterator.

     reset_key(self):
        Resets the key attribute in the view.

     append(self, instance: object):
        Appends an instance of ClassView or Field to the _lines list or updates the current dictionary.

     delete_dublicates(self):
        Removes duplicate entries from the _lines list based on their _id.

     copy(self):
        Creates and returns a deep copy of the current instance.

     __next__(self):
        Returns the next line in the _lines list when used as an iterator.

     ___str__(self):
        Returns a string representation of the instance.

     __repr__(self):
        Returns a string representation for debugging.

     @property
     def r(self):
        Returns the request from the view.

     async def init(self, params: dict | None = None, join_related: bool = False,
                    data: list | dict = None, exclude: list = [], schema: BaseModel = None) -> None:
        Extracts and initializes data based on input parameters and request data.

     def _get_view_vars_by_fieldinfo(self, fielinfo: FieldInfo | None = None) -> ViewVars:
        Returns a ViewVars instance initialized with field info attributes or default values.

     _get_view_vars(self, fieldname: str, is_filter: bool) -> dict[str, ViewVars]:
        Compiles and returns a dictionary of ViewVars based on specified field names and filter conditions.
    """
    _id: int
    _lsn: int | None = None
    _view: View
    _exclude: list
    _lines: list
    __state: int = 0
    _templates = {
        'as_tr_': 'line/as_tr.html',
    }
    p: P
    h: H

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if isinstance(other, ClassView):
            return self._id == other._id
        return False

    def reset_key(self):
        self._view.key = _get_key()

    def append(self, instance: object):
        if not self._lines:
            self.__dict__.update(instance.__dict__)
        elif isinstance(instance, ClassView):
            self._lines.append(instance)
        elif isinstance(instance, Field):
            self._lines.append(instance.cls)

    def delete_dublicates(self):
        ids: list[str] = []
        to_del_inxs: list[int] = []
        for indx, line in enumerate(self._lines):
            if line._id in ids:
                to_del_inxs.append(indx)
            else:
                ids.append(line._id)
        self._lines = [item for i, item in enumerate(self._lines) if i not in to_del_inxs]

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

    def __iter__(self):
        return self

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
                 model: str | BaseModel | BasicModel,
                 params: Optional[dict] = None,
                 exclude: list = [],
                 join_related: bool = False,
                 join_fields: list | None = None,
                 vars: dict | None = None,
                 parent_field: 'Field' = None
                 ):
        self.p = P()
        self.p.cls = self
        self.h = H()
        self.h.cls = self
        self._id = id(self)
        self._view = View()
        if not isinstance(model, str):
            if issubclass(model, BaseModel):  # type: ignore
                action_name = model.__name__  # type: ignore
                self._view.model = Model(
                    name=action_name,
                    _adapter=None,
                    _service=None,
                    domain=None,
                    schemas={
                        'create': model,
                        'update': model,
                        'get': model,
                        'filter': model,
                        'delete': model
                    },
                    model=action_name
                )
        else:
            self._view.model = request.scope['env'][model]
            self._view.actions = self._view.model.adapter.get_actions()
        self._view.request = request
        assert self._view.model, 'Model is not defined'
        self._view.model_name = self._view.model.name
        self._view.env = request.scope['env']
        self._view.key = _get_key()
        self._view.exclude = exclude or []
        self._view.params = params
        self._view.join_related = join_related
        self._view.join_fields = join_fields or []
        self._view.submodels = {}
        self._view.parent_field = parent_field
        config_sort = self._view.model.sort
        if config_sort:
            self._view.sort = {v: i for i, v in enumerate(config_sort)}
        else:
            self._view.sort = {}
        ##=======--------
        self._lines = []
        self._exclude = []
        self._exclude = exclude
        self._get_schema_fields()

    def __repr__(self):
        return f'<ClassView {self.v.model.name}'

    @property
    def r(self):
        return self.v.request

    async def init(self, params: Optional[dict] = None, data: Optional[list | dict] = None,
                   exclude: Optional[list] = None) -> None:
        """Майнинг данных по params"""
        self._exclude = exclude or []
        if isinstance(data, list):
            data = {i.get('id', uuid.uuid4()): i for i in data}
        await self.get_data(params=params or {}, data=data)

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
        view_vars_dict: dict[str, Any] = {}
        view_vars_dict.update({
            'required': fielinfo.is_required() if isinstance(fielinfo, FieldInfo) else False,
            'description': fielinfo.description,
            'title': fielinfo.title or str(fielinfo),
        })
        if isinstance(fielinfo.json_schema_extra, dict):
            view_vars_dict.update({
                'hidden': fielinfo.json_schema_extra.get('hidden', False),
                'color_map': fielinfo.json_schema_extra.get('color_map', {}),
                'readonly': fielinfo.json_schema_extra.get('readonly', False),
                'filter': fielinfo.json_schema_extra.get('filter', {}),
                'table': fielinfo.json_schema_extra.get('table', False),
                'form': fielinfo.json_schema_extra.get('form', False),
            })
        else:
            view_vars_dict.update({
                'hidden': False,
                'color_map': {},
                'readonly': True,
                'filter': {},
                'table': False,
                'form': False,
            })
        return ViewVars(**view_vars_dict)

    @lru_cache(maxsize=None)
    def _get_view_vars(self, fieldname: str, is_filter: bool) -> dict[str, ViewVars]:
        """Костыльный метод собирания ViewVars"""
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

    def _get_field(self, field_name: str, fields_merged: dict) -> 'Field':
        """
            Преобразование поля из Pydantic(Field) в схему Field для HTMX
        """
        fielinfo: FieldInfo = fields_merged[field_name]
        res: str = ''
        model: Model | None | BaseModel = None
        model_name: str = self._view.model.name
        is_filter: bool = True if self._view.model.schemas.filter.model_fields.get(
            field_name) else False  # type: ignore
        submodel: ClassView | None = None
        if not isinstance(fielinfo, ComputedFieldInfo):
            class_types: list = get_types(fielinfo.annotation, [])
        else:
            class_types = []
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
            elif field_name == 'search':
                res += 'search'
                break
            elif issubclass(c, enum.Enum):  # type: ignore
                res += 'enum'
            elif issubclass(c, BasicModel):  # type: ignore
                try:
                    model_name = c.Config.orm_model.__tablename__  # type: ignore
                except Exception as ex:
                    model_name = c.Config.__name__.lower()  # type: ignore
                res += 'rel'
                model = self._view.env[model_name]
                submodel = ClassView(
                    request=self._view.request,
                    model=model_name
                )
                self._view.submodels.update({field_name: submodel})
            elif issubclass(c, BaseModel):
                model_name = c.__name__.lower()  # type: ignore
                res += 'rel'
                model = c
                submodel = ClassView(
                    request=self._view.request,
                    model=c,
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
            '_field_name': field_name,
            'is_reserved': True if field_name in reserved_fields else False,
            'type': res,
            'fieldinfo': fielinfo,
            'model_name': model_name.lower(),
            'sort_idx': self._view.sort.get(field_name, 999),
            'cls': self,
            'val': submodel
        })
        if submodel:
            submodel.v.parent_field = field
        return field

    @lru_cache(maxsize=None)
    def _get_schema_fields(self) -> Fields:
        """Переделывает Pydantic схему на Схему для рендеринга в HTMX и Jinja2 - а зачем?"""
        fields: list[tuple[str, Field]] = []
        n = 0
        fields_merged = self._view.model.schemas.get.model_fields | self._view.model.schemas.get.model_computed_fields | self._view.model.schemas.filter.model_fields
        for k, v in fields_merged.items():
            if k in self._exclude:
                continue
            f = self._get_field(field_name=k, fields_merged=fields_merged)
            fields.append((k, f))
            n += 1
        fields = sorted(fields, key=lambda x: x[1].sort_idx)
        for field_name, field in fields:
            setattr(self, field_name, field)

    async def get_data(self, params: Optional[dict] = None, data: list | dict | None = None, ) -> None:
        """Метод собирает данные для конструктора модели"""

        if not params:
            params = self._view.params or {}
        if not data:
            if not self._view.model.adapter.domain.domain_type == 'INTERNAL':
                async with self._view.model.adapter as a:  # type: ignore
                    resp_data = await a.list(params=params)
                    data = resp_data['data']
            else:
                data_obj = await self.v.model.service.list(_filter=params)
                data = [i.__dict__ for i in data_obj]
        if isinstance(data, list):
            self._view.data = {i['id']: i for i in data}
        else:
            self._view.data = data if data is not None else {}
        await self.fill_lines(self._view.data, self.v.join_related, self.v.join_fields)

    async def fill_lines(self, data: dict | list, join_related: bool = False,
                         join_fields: list = []):
        if isinstance(data, list):
            data = {i.get('id', uuid.uuid4()): i for i in data}
        if not data:
            data = {}
        self._view.data = data
        self.join_fields: list[Any] = join_fields if join_fields is not None else []
        for _id, row in data.items():
            line_copied = self.copy() if self._lines else self
            line_copied._id = row.get('id', id(line_copied))
            line_copied._lsn = row.get('lsn')
            for col in line_copied.get_fields():
                val = row.get(col._field_name, None)
                if col.type in ('date', 'datetime'):
                    if isinstance(val, datetime):
                        pass
                    elif isinstance(val, str):
                        val = datetime.fromisoformat(val)
                elif col.type == 'id':
                    if not val:
                        val = []
                elif col.type.endswith('list_rel'):
                    submodel = line_copied.v.submodels[col._field_name].copy()
                    val = await submodel.fill_lines(data=val, join_related=False)
                    submodel.v.key = col.key
                    submodel.v.parent_field = col
                elif col.type.endswith('rel'):
                    submodel = line_copied.v.submodels[col._field_name].copy()
                    submodel._lines = []
                    val = await submodel.fill_lines(data=[val], join_related=False)
                    submodel.v.key = col.key
                    submodel.v.parent_field = col
                col.val = val
            line_copied._lines.append(line_copied)

        # if join_related or join_fields:
        #     missing_fields = defaultdict(list)
        #     for _line in self.lines:
        #         """Достаем все релейтед обьекты у которых модуль отличается"""
        #         assert _line.fields, "Проверяем что все поля есть"
        #         for field_name, field in _line.fields.get_fields():
        #             if field.type in ('uuid',):
        #                 # if field.widget.get('table'):  # TODO: может все надо а не ток table
        #                 if not join_fields:
        #                     missing_fields[field._field_name].append((field.val, field))
        #                 elif field._field_name in join_fields:
        #                     missing_fields[field._field_name].append((field.val, field))
        #     to_serialize = []
        #     for miss_key, miss_value in missing_fields.items():
        #         # _data = []
        #         _vals, _fields = [i[0] for i in miss_value], [i[1] for i in miss_value]
        #         miss_value_str = ''
        #         _corutine_data = None
        #         if isinstance(_vals, list):
        #             miss_value_str = ','.join([i for i in set(_vals) if i])
        #         if miss_value_str:
        #             qp = {'id__in': miss_value_str}
        #             _corutine_data = asyncio.create_task(
        #                 self.cls.env[_fields[0].model_name].adapter.list(params=qp))
        #         to_serialize.append((_vals, _fields, _corutine_data))
        #     for _vals, _fields, _corutine_data in to_serialize:
        #         _join_lines = {}
        #         if _corutine_data:
        #             _data = await _corutine_data
        #             _join_lines = {i['id']: i for i in _data['data']}
        #         for _val, _field in zip(_vals, _fields):
        #             if isinstance(_val, list):
        #                 _new_vals = []
        #                 for _v in _val:
        #                     __val = _join_lines.get(_v)
        #                     if __val:
        #                         _new_vals.append(__val)
        #                 _field.val = _new_vals
        #             else:
        #                 _field.val = _join_lines.get(_val)
        #             if _field.type == 'uuid':
        #                 _field.type = 'rel'
        #             elif _field.type == 'list_uuid':
        #                 _field.type = 'list_rel'
        #             else:
        #                 raise HTMXException(
        #                     status_code=500,
        #                     detail=f'Wrong field name {_field._field_name} in table model {_field.model}'
        #                 )
        #     for col in missing_fields.keys():
        #         for _field_name, _header_col in self.line_header.fields.get_fields():  # type: ignore
        #             if col == _field_name:
        #                 _header_col.type = _header_col.type.replace('uuid', 'rel')
        #                 _header_col.type = _header_col.type.replace('list_uuid', 'list_rel')
        return self

    def get_fields(self, display_view: Optional[str] = None, method: MethodType = MethodType.GET) -> Fields:
        fields = [k for i, k in self.__dict__.items() if isinstance(k, Field) and k._field_name not in self._exclude]
        return _crud_filter(fields, method, display_view)

    def render_line(self, template: str, block_name: str, method: MethodType = MethodType.GET) -> str:
        """Рендеринг подразумеваем 1 лайны из шаблона"""
        return render_block(
            environment=environment,
            template_name=template,
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
            cls=self,
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

    async def update_line(self, data: dict, id: uuid.UUID) -> 'ClassView':
        """Метод обновления обьектов"""
        new_data = []
        try:
            method_schema_obj = self.v.model.schemas.update(**data)
        except ValidationError as e:
            raise HTTPException(status_code=406, detail=f"Error: {str(e)}")
        _json = method_schema_obj.model_dump(mode='json', exclude_unset=True)
        line = await self.v.model.adapter.update(id=id, json=_json)
        new_data.append(line)
        await self.fill_lines(new_data)
        return self

    async def create_line(self, data: dict) -> 'ClassView':
        """Метод создания обьектов"""
        new_data = []
        try:
            method_schema_obj = self.v.model.schemas.create(**data)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())  # type: ignore
        _json = method_schema_obj.model_dump(mode='json', exclude_unset=True)
        line = await self.v.model.adapter.create(json=_json)
        new_data.append(line)
        await self.fill_lines(new_data)
        return self

    async def get_action(self, action_name: str, line_id: uuid.UUID) -> str:
        """Метод отдает апдейт схему , те столбцы с типами для HTMX шаблонов"""
        action = self.v.actions[action_name]
        action_schema = ClassView(
            request=self.v.request,
            model=action['schema'],
        )
        return render_block(
            environment=environment,
            template_name=f'cls/action.html', line_id=line_id, model=self.v.model.name,
            block_name='action', cls=action_schema, action=action
        )


class Method(str, enum.Enum):
    GET: str = 'get'  # Дать запись на чтение
    CREATE: str = 'create'  # Дать запись на создание
    UPDATE: str = 'update'  # Дать запись на изменение
    DELETE: str = 'delete'  # Дать запись на удаление
    UPDATE_SAVE: str = 'save'  # Сохранить изменения
    CREATE_SAVE: str = 'save_create'  # Сохранить новую запись
    DELETE_SAVE: str = 'delete_delete'  # Подтвердить удаление записи
