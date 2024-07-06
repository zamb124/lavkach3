from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MethodType(str, Enum):
    CREATE = 'create'
    UPDATE = 'update'
    GET = 'get'
    DELETE = 'delete'



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

