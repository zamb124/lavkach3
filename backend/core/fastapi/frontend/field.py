from enum import Enum
from typing import Optional, Any

from jinja2_fragments import render_block
from pydantic import BaseModel

from core.fastapi.frontend.enviroment import environment
from core.fastapi.frontend.types import ViewVars, MethodType


class FieldFields:
    model_name: str  # Имя поля
    vars: Optional[dict] = None  # Переменные если нужно передать контекст


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
    line: Optional[Any] = None  # Обьект, которому принадлежит поле
    lines: Optional[Any] = None  # Если поле list_rel, то субобьекты
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
    def as_update(self):
        """
            Отобразить поле с возможностью редактирования
        """
        return self.render(block_name='as_update')

    @property
    def as_get(self):
        """
            Отобразить поле только на чтение
        """
        return self.render(block_name='as_get')

    @property
    def as_table_get(self):
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
    def as_table_update(self):
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
