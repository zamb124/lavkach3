import copy
from enum import Enum
from typing import Optional, Any
from typing import TYPE_CHECKING

from jinja2_fragments import render_block, render_block_async
from pydantic.fields import FieldInfo
from watchfiles import awatch

from core.frontend.enviroment import environment
from core.frontend.types import MethodType, ViewVars
from core.frontend.utils import get_types

if TYPE_CHECKING:
    from core.frontend.constructor import ClassView


class FieldFields:
    model_name: str  # Имя поля
    vars: Optional[dict] = None  # Переменные если нужно передать контекст


class Field:
    """
        Описание поля
        - as_update - виджет поля как редактируемого
        - as_get - виджет поля как просмотра
        - as_table_update - виджет как таблица (доступен только для list_rel) полей
        - as_table_get - виджет как таблица (доступен только для list_rel) полей
    """
    cls: 'ClassView'  # Класс, которому принадлежит поле
    fieldinfo: 'FieldInfo'  # Информация о поле
    _field_name: str  # Системное имя поля
    type: str  # Тип поля (srt, ins, rel, list_rel ... )

    sort_idx: int = 0  # Индекс сортировки поля

    is_filter: bool = False  # Является ли поле фильтром
    is_reserved: bool = False  # Призна
    # Views vars
    get: ViewVars
    create: ViewVars
    update: ViewVars
    val: Any = None

    def copy(self) -> 'Field':
        instance = copy.copy(self)
        instance.val = None
        return instance

    def __call__(self, *args, **kwargs):
        return self.val

    def __iter__(self):
        from core.frontend.constructor import ClassView
        if isinstance(self.val, ClassView):
            return self.val
        else:
            return self.val.__iter__()

    def __eq__(self, other):
        if isinstance(other, Field):
            return id(self) == id(other)
        else:
            return self.val == other

    def __next__(self):
        from core.frontend.constructor import ClassView
        """Если использовать конструктор как итератор, то он будет возвращать строки"""
        if isinstance(self.val, ClassView):
            try:
                line = self.val._lines[self.val.__state]
                self.val.__state += 1
                return line
            except IndexError:
                self.val.__state = 0
                raise StopIteration
        else:
            next(self.val)

    def __getattr__(self, name):
        from core.frontend.constructor import ClassView
        if name == 'val' and isinstance(self.val, ClassView):
            return self.val
        if isinstance(self.val, ClassView):
            return getattr(self.val, name)
        if name == 'val':
            return self.val
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return f'<Field {self.cls.v.model.name} - {self._field_name}>'

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    @property
    async def enum(self):
        if isinstance(self.fieldinfo.annotation, Enum):
            return self.fieldinfo.annotation
        else:
            for type in get_types(self.fieldinfo.annotation, []):
                if issubclass(type, Enum):
                    return type

    @property
    async def field_name(self):
        if self.cls.v.parent_field:
            if isinstance(self.cls.v.parent_field, Field):
                return f'{self.cls.v.parent_field._field_name}[{self.cls.p.lsn}][{self._field_name}]'
            elif isinstance(self.cls.v.parent_field, str):
                return f'{self.cls.v.parent_field}[{self.cls.p.id}][{self._field_name}]'
        return self._field_name

    @property
    async def key(self) -> str:
        """Отдает уникальный идентификатор для поля"""
        return f'{self.cls.p.key}--{self._field_name}'

    async def as_(self, method='get', button=False, model=None):
        """Отдает виджет поля в зависимости от метода"""
        widget = None
        match method:
            case 'get':
                widget = self.as_get
            case 'update':
                widget = self.as_update
            case 'create':
                widget = self.as_create
        bar = await self.as_update_link(method)
        if button:
            return f"""<div id="{self.key}" style="display: flex; justify-content: center; align-items: center;">{widget}{bar}</div>"""
        else:
            return widget

    @property
    def description(self) -> str:
        return self.fieldinfo.description or self._field_name

    async def render(self, block_name: str, method: MethodType = MethodType.GET) -> str:
        """Метод рендера шаблона"""
        type = self.type or 'str'
        rendered_html = await render_block_async(
            environment=environment,
            template_name=f'field/{type}.html',
            block_name=block_name,
            field=self,
            method=method,
        )
        return rendered_html

    @property
    async def label(self) -> str:
        """Отдать Label for шаблон для поля"""
        return await render_block_async(  # type: ignore
            environment=environment,
            template_name=f'field/label.html',
            block_name='label',
            field=self,
        )

    async def as_update_link(self, method='get') -> str:
        """Отдать кнопку для запросы формы as_update"""
        return await render_block_async(
            environment=environment,
            template_name=f'field/as_update_link.html',
            block_name=method,
            field=self,
        )

    async def as_card(self, url=None, model=None):
        """Отобразить как маленькую карточку"""
        return await render_block_async(
            environment=environment,
            template_name=f'field/as_card.html',
            block_name='as_card',
            field=self,
            url=url,
            movel=model
        )

    async def as_a(self, url=None, model=None):
        """Отдать ссылку, только для uuid и rel"""
        return await render_block_async(
            environment=environment,
            template_name=f'field/as_a.html',
            block_name='as_a',
            field=self,
            url=url,
            model=model
        )

    @property
    async def data_key(self) -> str:
        """Отдать Label for шаблон для поля"""
        return f't-{self.cls.v.model.name}-{self._field_name}'

    @property
    async def data_key_description(self) -> str:
        """Отдать Label for шаблон для поля"""
        return f't-{self.cls.v.model.name}-{self._field_name}-description'

    @property
    async def as_update(self) -> str:
        """Отобразить поле с возможностью редактирования"""
        return await self.render(block_name='as_update', method=MethodType.UPDATE)

    @property
    async def as_create(self) -> str:
        """Отобразить поле с возможностью редактирования"""
        return await self.render(block_name='as_create', method=MethodType.CREATE)

    @property
    async def as_get(self) -> str:
        """Отобразить поле только на чтение"""
        return await self.render(block_name='as_get')

    @property
    async def as_card_title(self) -> str:
        """Отобразить поле только на чтение"""
        return await self.render(block_name='as_card_title')

    @property
    async def as_th_title(self):
        return await render_block_async(
            environment=environment,
            template_name=f'field/as_th_title.html',
            block_name='th_title',
            field=self,
        )

    @property
    async def as_table_get(self) -> str:
        """Отобразить поле как Таблицу (Если поле является list_rel)
            Нужно обязательно передавать какому обьекту принадлежит лайна
        """
        return await render_block_async(
            environment=environment,
            template_name=f'cls/as_table.html',
            block_name='get',
            method=MethodType.GET,
            line=self.val,
            parent=self.cls.v.parent_field
        )

    @property
    async def as_table_update(self) -> str:
        """Отобразить поле как Таблицу на редактирование (Если поле является list_rel)
            Нужно обязательно передавать какому обьекту принадлежит лайна
        """
        block_name = 'get'
        return await render_block_async(
            environment=environment,
            template_name=f'cls/as_table.html',
            block_name=block_name,
            method=MethodType.UPDATE,
            line=self.val,
            parent=self.cls.v.parent_field
        )

    async def filter_as_string(self) -> str:
        """Костыльная утилита, что бы в js передать фильтр"""
        return self.update.get('filter')


class Fields:
    """Обертка для удобства, что бы с полями работать как с обьектом"""
    _fields: list = []
    __state = 0  # счетчик итераций

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def __iter__(self):
        self._fields = [i for i in self.__dict__.values() if isinstance(i, Field)]
        return self

    def __next__(self):
        """Если использовать конструктор как итератор, то он будет возвращать строки"""
        try:
            field = self._fields[self.__state]
            self.__state += 1
            return field
        except IndexError:
            self.__state = 0
            raise StopIteration

    def get_fields(self):
        return {i._field_name: i for i in self._fields}.items()
