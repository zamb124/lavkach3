import copy
import json
from enum import Enum
from typing import Optional, Any

from jinja2_fragments import render_block
from pydantic import BaseModel


from core.frontend.enviroment import environment
from core.frontend.types import MethodType, ViewVars


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
    field_name: str  # Системное имя поля
    type: str  # Тип поля (srt, ins, rel, list_rel ... )

    # widget params
    enums: Optional[Any] = None  # Если поле enum, то тут будет список енумов
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

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def key(self) -> str:
        """Отдает уникальный идентификатор для поля"""
        return f'{self.cls.p.key}--{self.field_name}'

    def render(self, block_name: str, type: str = '', method: MethodType = MethodType.GET) -> str:
        """Метод рендера шаблона"""
        type = type or self.type
        rendered_html = render_block(
            environment=environment,
            template_name=f'field/{type}.html',
            block_name=block_name,
            field=self,
            method=method,
        )
        return rendered_html

    @property
    def label(self) -> str:
        """Отдать Label for шаблон для поля"""
        return render_block(
            environment=environment,
            template_name=f'field/label.html',
            block_name='label',
            field=self,
        )

    @property
    def as_card(self):
        """Отобразить как маленькую карточку"""
        return render_block(
            environment=environment,
            template_name=f'field/as_card.html',
            block_name='as_card',
            field=self,
        )

    def as_a(self, url=None, model=None):
        """Отдать ссылку, только для uuid и rel"""
        return render_block(
            environment=environment,
            template_name=f'field/as_a.html',
            block_name='as_a',
            field=self,
            url=url,
            model=model
        )

    @property
    def data_key(self) -> str:
        """Отдать Label for шаблон для поля"""
        return f't-{self.cls.v.model.name}-{self.field_name}'

    @property
    def as_update(self) -> str:
        """Отобразить поле с возможностью редактирования"""
        return self.render(block_name='as_update', method=MethodType.UPDATE)

    @property
    def as_create(self) -> str:
        """Отобразить поле с возможностью редактирования"""
        return self.render(block_name='as_create', method=MethodType.CREATE)

    @property
    def as_get(self) -> str:
        """Отобразить поле только на чтение"""
        return self.render(block_name='as_get')

    @property
    def as_card_title(self) -> str:
        """Отобразить поле только на чтение"""
        return self.render(block_name='as_card_title')

    @property
    def as_table_get(self) -> str:
        """Отобразить поле как Таблицу (Если поле является list_rel)
            Нужно обязательно передавать какому обьекту принадлежит лайна
        """
        return render_block(
            environment=environment,
            template_name=f'cls/as_table.html',
            block_name='get',
            method=MethodType.GET,
            line=self.val,
            parent=self.cls.v.parent_field
        )

    @property
    def as_table_update(self) -> str:
        """Отобразить поле как Таблицу на редактирование (Если поле является list_rel)
            Нужно обязательно передавать какому обьекту принадлежит лайна
        """
        block_name = 'get'
        return render_block(
            environment=environment,
            template_name=f'cls/as_table.html',
            block_name=block_name,
            method=MethodType.UPDATE,
            line=self.val,
            parent=self.cls.v.parent_field
        )

    def filter_as_string(self) -> str:
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
        return {i.field_name: i for i in self._fields}.items()
