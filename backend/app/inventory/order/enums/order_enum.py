from enum import Enum

from . import BaseEnum
from ...location.enums import VirtualLocationZones, PhysicalLocationClass


class StoreEnum(BaseEnum):
    pass


class EstatusTerminal(str, Enum):
    """
     estatus это по своей сути отражение текущей работы над обьектом, если какой то метод сейчас производит какую
     то работу, то он должен установить статус
    """
    FAILED: str = 'failed'  # Переход не удался
    DONE:   str = 'done'  # Переход выполнен


class MoveStatus(str, Enum):
    CREATED: str = 'created'  # Мув создан, но не подтвержден
    CONFIRMED: str = 'confirmed'  # Мув пдтвержден и нужные кванты найдены и зарезервированы
    WAITING: str = 'waiting'  # Ожидает назначения оператора
    PROCESSING: str = 'processing'  # Оператор начал действия
    COMPLETE: str = 'done'  # Оператор завершил действия
    CANCELED: str = 'canceled'  # Отменен, кванты при этом разрезерируются
    FAILED: str = 'failed'  # Резервирование не удалось


class MoveType(str, Enum):
    """
    Типа Move означает это перемещение упаковкой или товара
    """
    PRODUCT: str = 'product'  # Означает что задание товарное, те перемещается часть товара
    PACKAGE: str = 'package'  # Перемещается упаковка вместе с товаром


class OrderStatus(str, Enum):
    CREATED: str = 'created'  # Мув создан, но не подтвержден
    CONFIRMED: str = 'confirmed'  # Мув пдтвержден и нужные кванты найдены и зарезервированы
    WAITING: str = 'waiting'  # Ожидает назначения оператора
    PROCESSING: str = 'processing'  # Оператор начал действия
    COMPLETE: str = 'done'  # Оператор завершил действия
    CANCELED: str = 'canceled'  # Отменен, кванты при этом разрезерируются
    FAILED: str = 'failed'  # Резервирование не удалось


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
    IN_LOCATION_SRC: str = 'in_location_src'  # саджест ввода/сканирования местоположения источника
    IN_LOCATION_DEST: str = 'in_location_dest'  # саджест ввода/сканирования местоположения источника
    IN_LOT: str = 'in_lot'  # ввод даты КСГ партии
    IN_RESOURCE: str = 'in_resource'  # сканирование ресурса
    IN_VALID: str = 'in_valid'  # ввод даны истечения срока годности, когда просто ввод а не создание партии
    NEW_PACKAGE: str = 'new_package'  # саджест создания новой package
    NEW_LOT: str = 'new_lot'  # саджест создания партии / не путать с in_valid


class SuggestStatus(str, Enum):
    WAITING: str = 'waiting'  # Ожидает подверждения
    DONE: str = 'done'  # Выполнен


class MoveLogType(str, Enum):
    RECEIPT: str = 'receipt_in'  # Приемка товара от внешнего источника (поставщика) или принимаем возврат от покупателя
    SHIPMENT: str = 'shipment_out'  # Отгрузка товара во внешний источник (покупателю) или возврат поставщику
    WRITE_OFF: str = 'writeoff_in'  # Списание товара
    LOST: str = 'lost_out'  # Потеря товара
    FOUND: str = 'found_in'  # Найден товар
    RECLASS_IN: str = 'reclass_in'  # Пересортица товара
    RECLASS_OUT: str = 'reclass_out'  # Пересортица товара
    PUT_IN: str = 'put_in'  # Положил товар (перемещение)
    PUT_OUT: str = 'put_out'  # Взял товар (перемещение)
    INVENROTY_IN: str = 'inventory_in'  # Инвентаризация
    INVENROTY_OUT: str = 'inventory_out'  # Инвентаризация


TYPE_MAP = {
    (VirtualLocationZones.PARTNER, PhysicalLocationClass.PLACE): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
    (VirtualLocationZones.PARTNER, PhysicalLocationClass.ZONE): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
    (VirtualLocationZones.PARTNER, PhysicalLocationClass.PLACE): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
    (PhysicalLocationClass.PLACE, PhysicalLocationClass.PLACE): (MoveLogType.PUT_OUT, MoveLogType.PUT_IN),
    (PhysicalLocationClass.PLACE, PhysicalLocationClass.ZONE): (MoveLogType.PUT_OUT, MoveLogType.PUT_IN),
    (PhysicalLocationClass.ZONE, PhysicalLocationClass.PLACE): (MoveLogType.PUT_OUT, MoveLogType.PUT_IN),
    (PhysicalLocationClass.ZONE, PhysicalLocationClass.ZONE): (MoveLogType.PUT_OUT, MoveLogType.PUT_IN),
    (PhysicalLocationClass.PLACE, VirtualLocationZones.PARTNER): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
    (PhysicalLocationClass.PLACE, VirtualLocationZones.INVENTORY): (
        MoveLogType.INVENROTY_OUT, MoveLogType.INVENROTY_IN),
    (VirtualLocationZones.INVENTORY, PhysicalLocationClass.PLACE): (
        MoveLogType.INVENROTY_OUT, MoveLogType.INVENROTY_IN),
    (VirtualLocationZones.LOST, PhysicalLocationClass.PLACE): (MoveLogType.LOST, MoveLogType.FOUND),
    (PhysicalLocationClass.PLACE, VirtualLocationZones.LOST): (MoveLogType.LOST, MoveLogType.FOUND),
    (PhysicalLocationClass.ZONE, VirtualLocationZones.PARTNER): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
    (PhysicalLocationClass.PLACE, VirtualLocationZones.PARTNER): (MoveLogType.SHIPMENT, MoveLogType.RECEIPT),
}
