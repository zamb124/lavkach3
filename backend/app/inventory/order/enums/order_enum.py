from enum import Enum

from core.fastapi.frontend.enums import TextColorEnum
from . import BaseEnum


class StoreEnum(BaseEnum):
    pass


class MoveStatus(str, Enum):
    CREATED: str = 'created'
    CONFIRMED: str = 'confirmed'
    WAITING: str = 'waiting'
    ASSIGNED: str = 'assigned'
    PROCESSING: str = 'processing'
    DONE: str = 'done'
    CANCELED: str = 'canceled'


move_color_map = {
    MoveStatus.CREATED: TextColorEnum.LIGHT,
    MoveStatus.CONFIRMED: TextColorEnum.DARK,
    MoveStatus.WAITING: TextColorEnum.WARNING,
    MoveStatus.ASSIGNED: TextColorEnum.INFO,
    MoveStatus.PROCESSING: TextColorEnum.SECONDARY,
    MoveStatus.DONE: TextColorEnum.SUCCESS,
    MoveStatus.CANCELED: TextColorEnum.DANGER,
}


class MoveType(str, Enum):
    """
    Типа Move означает это перемещение упаковкой или товара
    """
    PRODUCT: str = 'product'  # Означает что задание товарное, те перемещается часть товара
    PACKAGE: str = 'package'  # Перемещается упаковка вместе с товаром


class OrderStatus(str, Enum):
    DRAFT: str = 'draft'
    WAITING: str = 'waiting'
    CONFIRMED: str = 'confirmed'
    ASSIGNED: str = 'assigned'
    DONE: str = 'done'
    CANCELED: str = 'canceled'


class OrderClass(str, Enum):
    """
    Класс ордера
    """
    INCOMING: str = 'incoming'  # Входящие
    OUTGOING: str = 'outgoing'  # Исходящий
    INTERNAL: str = 'internal'  # Внутрислкдской


class BackOrderAction(str, Enum):
    """
    Поведение бекордера
    """
    ASK: str = 'ask'  # Спросить нужен ли Ордер на возврат
    ALWAYS: str = 'always'  # Нельзя спросить он создается сам
    NEVER: str = 'never'  # Не создавать


class ReservationMethod(str, Enum):
    """
    Тип медода резервирования
    """
    AT_CONFIRM: str = 'at_confirm'  # При утверждении
    MANUAL: str = 'manual'  # Вручную запустить резервирование
    AT_DATE: str = 'at_date'  # В определенную дату, но она должна быть не меньше planned_date, иначе запустится само
    TIME_BEFORE_DATE: str = 'time_before_date'  # За определенное количество минут до начала planned_date


class MoveLogType(str, Enum):
    GET: str = 'get'  # Взял квант
    PUT: str = 'put'  # Положил квант
    RES: str = 'res'  # Зарезервировал квант
    UNR: str = 'unr'  # Разрезервировал квант


class SuggestType(str, Enum):
    IN_QUANTITY: str = 'in_quantity'  # Саджест ввода количества (те на экране нужно ввести какуюто цифру)
    IN_PRODUCT: str = 'in_product'  # саджест ввода/сканирования идентификатора товара
    IN_PACKAGE: str = 'in_package'  # саджест ввода/сканирования идентификатора упаковки
    IN_LOCATION: str = 'in_location'  # саджест ввода/сканирования местоположения(location)
    IN_LOT: str = 'in_lot'  # ввод даты КСГ партии
    IN_RESOURCE: str = 'in_resource'  # сканирование ресурса
    IN_VALID: str = 'in_valid'  # ввод даны истечения срока годности, когда просто ввод а не создание партии
    NEW_PACKAGE: str = 'new_package'  # саджест создания новой package
    NEW_LOT: str = 'new_lot'  # саджест создания партии / не путать с in_valid


class SuggestStatus(str, Enum):
    WAITING: str = 'waiting'  # Ожидает подверждения
    DONE: str = 'done'  # Выполнен
