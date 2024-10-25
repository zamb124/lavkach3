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
    field_name: str  # Системное имя поля
    type: str  # Тип поля (srt, ins, rel, list_rel ... )
    model_name: str  # Наименование модели
    domain_name: str  # Наименование домена модели
    # widget params
    enums: Optional[Any] = None  # Если поле enum, то тут будет список енумов
    sort_idx: int = 0  # Индекс сортировки поля
    line: Optional[Any] = None  # Обьект, которому принадлежит поле
    lines: Optional[Any] = None  # Если поле list_rel, то субобьекты

    is_filter: bool = False  # Является ли поле фильтром
    is_reserved: bool = False  # Призна
    # Views vars
    get: ViewVars
    create: ViewVars
    update: ViewVars
    val: Any

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def js(self):
        di = self.__dict__
        di['update'] = self.update.model_dump(mode='json')
        di['get'] = self.get.model_dump(mode='json')
        di['create'] = self.create.model_dump(mode='json')
        di.pop('lines')
        di.pop('line')
        return json.dumps(di)

    @property
    def key(self) -> str:
        """Отдает уникальный идентификатор для поля"""
        return f'{self.line.key}--{self.field_name}'

    def render(self, block_name: str, type: str = '', backdrop: list = []) -> str:
        """Метод рендера шаблона"""
        type = type or self.type
        rendered_html = render_block(
            environment=environment,
            template_name=f'field/{type}.html',
            block_name=block_name,
            field=self,
            backdrop=backdrop
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
    def as_update(self) -> str:
        """Отобразить поле с возможностью редактирования"""
        return self.render(block_name='as_update')

    @property
    def as_get(self) -> str:
        """Отобразить поле только на чтение"""
        return self.render(block_name='as_get')

    @property
    def as_table_get(self) -> str:
        """Отобразить поле как Таблицу (Если поле является list_rel)"""
        return render_block(
            environment=environment,
            template_name=f'cls/table.html',
            block_name='as_table',
            method=MethodType.GET,
            cls=self
        )

    @property
    def as_table_update(self) -> str:
        """Отобразить поле как Таблицу на редактирование (Если поле является list_rel)"""
        block_name = 'as_table'
        return render_block(
            environment=environment,
            template_name=f'cls/table.html',
            block_name=block_name,
            method=MethodType.UPDATE,
            cls=self
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
