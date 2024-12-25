import os
from types import UnionType
from typing import Annotated, Union, Optional
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    from core.frontend.field import Fields, MethodType

path = os.path.dirname(os.path.abspath(__file__))

template_dirs = [
    'core/frontend/templates',
]

# Создайте загрузчик файловой системы с несколькими директориями
loader = FileSystemLoader(template_dirs)

# Создайте окружение Jinja2 с указанным загрузчиком
environment = Environment(loader=loader, enable_async=True, autoescape=False)


def _crud_filter(fields: 'Fields', method: 'MethodType', display_view: Optional[str] = None):
    """
        Jinja2 флильтр, который фильтрует строки для типа отображений
        ВАЖНО: Если table и в схеме 'get' True, то поле будет отображаться в таблице в любом режиме
    """
    res = []
    for field in fields:
        method_type = getattr(field, method.value)
        if display_view == 'filter':
            if field.is_filter:
                res.append(field)
        elif not display_view:
            res.append(field)
        elif getattr(method_type, display_view):
            res.append(field)
        else:
            if display_view == 'table':
                if getattr(field.get, 'table'):
                    res.append(field)

    return res
    #return [v for v in fields if getattr(getattr(v, method.value), display_view)]


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
    'company_id',
    'id'
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
