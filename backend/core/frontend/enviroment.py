import os
from types import UnionType
from typing import Annotated, Union
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.frontend.field import Fields, MethodType

path = os.path.dirname(os.path.abspath(__file__))

environment = Environment(
    loader=FileSystemLoader(f"{path}/templates/"),
    autoescape=select_autoescape(("html", "jinja2"))
)



def _crud_filter(fields: 'Fields', method: 'MethodType', display_view: str = 'table'):
    """
        Jinja2 флильтр, который фильтрует строки для типа отображений
    """
    res = []
    for field in fields:
        if field.field_name == 'id':
            a=1
        method_type = getattr(field, method.value)
        if getattr(method_type, display_view):
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
