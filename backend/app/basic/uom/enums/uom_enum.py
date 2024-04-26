from enum import Enum

from . import BaseEnum


class StoreEnum(BaseEnum):
    pass


class UomType(str, Enum):
    SMALLER: str = 'smaller'
    STANDART: str = 'standart'
    BIGGER: str = 'bigger'