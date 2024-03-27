import enum
import uuid
from enum import Enum
from typing import Optional
import datetime
from sqlalchemy import Column, Unicode, Sequence, Uuid, ForeignKey, DateTime, func, text, UniqueConstraint, ARRAY
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin, guid, guid_primary_key
from app.inventory.quant.models import Lot
#from app.inventory.location.models import Location, LocationClass
from app.inventory.location.enums import LocationClass, PutawayStrategy


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
    ASK:    str = 'ask'         # Спросить нужен ли Ордер на возврат
    ALWAYS: str = 'always'      # Нельзя спросить он создается сам
    NEVER:  str = 'never'       # Не создавать


class ReservationMethod(str, Enum):
    """
    Тип медода резервирования
    """
    AT_CONFIRM:         str = 'at_confirm'                  # При утверждении
    MANUAL:             str = 'manual'                      # Вручную запустить резервирование
    AT_DATE:            str = 'at_date'                     # В определенную дату, но она должна быть не меньше planned_date, иначе запустится само
    TIME_BEFORE_DATE:   str = 'time_before_date'            # За определенное количество минут до начала planned_date


class OrderType(Base, AllMixin):
    """
    Order Type - Тип складского задания, определяет поведение складсхих заданий при создании или выполнении
    такие как :
     -+ Какие зоны источника складское задание будет использовать для резервирования по умолчанию( может быть пустым, значит задается либо вручную, либо согласно стратегии для выбранного товара)
     -+ Список зон исключения для поиска зон обратная аналоги с предыдущим утверждением
     -+ Какие зоны назначение складское задание будет использовать по умолчанию( может быть пустым, значит задается либо вручную, либо согласно стратегии для выбранного товара)
     -+ Список зон исключения для поиска зон обратная аналоги с предыдущим утверждением
     -+ Какое складское задание создавать на остаток, если задание выполнено не в полном обьеме
     -+ Метод резервирования (при утверждении, вручную, на опередленную дату и время, или за определенное время до начала запланированной)
     -+ Список зон (по порядку) в которых задание будет искать товар (не выбрано, значит все внутренние зоны)
     - Типы упаковки по порядку с которыми работает Ордер, например  если ничего не выбрано - Ордер ищет обсалютно все товары в выбранных зонах/локация или только в определенных типах упаковки
     если выбрано, то будет искать в рамках данных упаковок и в той последовательности (ВАЖНО!) типы упаковках могут быть строго заданы в локациях, тогда приоритетом будет правила локации
     -+ Исключающие типы упаковок
     -+ Гомогенность - это означает, что в упаковки сборщика не может быть 1 товар из 2х разных партий, те что бы физически партии не могли быть в 1 местоположении
     - Разрешать на ходу создавать упаковки для товаров, те кладовщик может на ресурсе создавтаь упаковки для товаров
     -+ Список допустимых типов упаковок
     -+ Список исключающих типов упаковок
     -+ Можно ли создавать данный тип ордера вручную
     -+ Можно ли Overdelivery (когда принес больше чем мог)
     -+ Может ли быть Оверколичество (когда например в складском задании физически оказалось товар больше, чем предпологалось)
     -+ Создатель/Исполнители

     Так же важно, что массив движений(Move) по сути своей наследует все спецификацию Order
    """
    __tablename__ = "order_type"
    __table_args__ = (
        UniqueConstraint('title', 'company_id', name='_order_type_companyid_title_uc'),
    )
    lsn_seq = Sequence(f'order_type_lsn_seq')
    prefix: Mapped[str] = mapped_column(index=True)                                                             # Префикс данных Ордеров
    title: Mapped[str] = mapped_column(index=True)                                                              # Человекочетабельное имя
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    order_class: Mapped[OrderClass]                                                                             # Класс ордера
    allowed_location_src_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)       # Разрешенные зоны для подбора
    exclusive_location_src_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)     # Искличенные зоны из подбора
    allowed_location_dest_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)      # Разрешенные зона для назначения
    exclusive_location_dest_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)    # Исключение зон из назначения
    backorder_order_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("order_type.id", ondelete='CASCADE'))# Тип Ордера возврата разницы
    backorder_action_type: Mapped[BackOrderAction] = mapped_column(default=BackOrderAction.ASK)                 # Поведение возврата разницы
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)                                     # Склад
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)                                   # Партнер (если у опредленного партнера своя стратегия)
    reservation_method: Mapped[ReservationMethod] = mapped_column(default=ReservationMethod.AT_CONFIRM)         # Метод резервирование
    reservation_time_before: Mapped[Optional[int]] = mapped_column(default=0)                                   # Минуты до начала резервирования
    allowed_package_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)            # Разрешенные типы упаковок
    exclusive_package_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)          # Исключение типы упаковок
    is_homogeneity: Mapped[bool]                                                                                   # Признак Гомогенности
    is_allow_create_package: Mapped[bool]                                                                          # Можно ли создавать упаковки
    is_can_create_order_manualy: Mapped[bool]                                                                      # Можно ли создавать Ордер вручную
    is_overdelivery: Mapped[bool]                                                                                  # Возможно ли Overdelivery
    created_by: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)                                   # Кем создан/изменен
    edited_by: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)                                    # Кем создан/изменен
    barcode: Mapped[str]                                                                                        # Штрих-код ордера для быстрого доступа
    strategy: Mapped['PutawayStrategy'] = mapped_column(default=PutawayStrategy.FEFO)                           # Стратегия комплектования

class OrderStatus(str, Enum):
    DRAFT:      str = 'draft'
    WAITING:    str = 'waiting'
    CONFIRMED:  str = 'confirmed'
    ASSIGNED:   str = 'assigned'
    DONE:       str = 'done'
    CANCELED:   str = 'canceled'


class Order(Base, AllMixin):
    """
    это складское задание(ордер), которое обьединяет в себе как общий документ основание
    так и складские движения (Move)
    Также в Ордере могут быть такие уточнения как
    """
    __tablename__ = "order"
    __table_args__ = (
        UniqueConstraint('external_number', 'company_id', name='_order_companyid_external_number_uc'),
    )
    lsn_seq = Sequence(f'order_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    number: Mapped[str] = mapped_column(index=True)    # Человекочитаемый номер присвается по формуле - {ГОД(2)}-{МЕСЯЦ}-{ДЕНЬ}-{LSN}
    order_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('order_type.id', ondelete='CASCADE'))
    order_type_rel: Mapped[OrderType] = relationship(lazy='selectin')
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("order.id", ondelete="CASCADE"))
    external_number: Mapped[Optional[str]]
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)
    lot_id: Mapped[Optional['Lot']] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"))
    origin_type: Mapped[Optional[str]] = mapped_column(index=True)
    origin_number: Mapped[Optional[str]] = mapped_column(index=True)
    planned_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    actual_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    edited_by: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    expiration_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    users_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)
    description: Mapped[Optional[str]]
    status: Mapped[OrderStatus] = OrderStatus.DRAFT
    move_list_rel: Mapped[Optional[list["Move"]]] = relationship(back_populates="order_rel", lazy="selectin")


class MoveStatus(str, Enum):
    DRAFT:      str = 'draft'
    WAITING:    str = 'waiting'
    CONFIRMED:  str = 'confirmed'
    PARTIALY:   str = 'partially'
    ASSIGNED:   str = 'assigned'
    DONE:       str = 'done'
    CANCELED:   str = 'canceled'

class MoveType(str, enum.Enum):
    """
    Типа Move означает это перемещение упаковкой или товара
    """
    PRODUCT: str = 'product' # Означает что задание товарное, те перемещается часть товара
    PACKAGE: str = 'package' # Перемещается упаковка вместе с товаром

class Move(Base, AllMixin):
    """
    Move - это часть Order, но определяющее уже конкретную позицию товара
    """
    __tablename__ = "move"
    lsn_seq = Sequence(f'move_lsn_seq')

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    type: Mapped[MoveType]
    move_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("move.id", ondelete='RESTRICT'))
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('order.id', ondelete='RESTRICT'))
    order_rel: Mapped[Order] = relationship(back_populates='move_list_rel')
    location_src_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    location_dest_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    lot_id: Mapped[Optional['Lot']] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"))
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    # ONE OF Возможно либо location_id либо product_id
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    quantity: Mapped[float]     # Если перемещение кпаковки, то всегда 0
    uom_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("uom.id", ondelete="RESTRICT"), index=True) # Если перемещение упаковкой то None
    status: Mapped[MoveStatus]


class MoveLogType(str, Enum):
    GET: str = 'get'        # Взял квант
    PUT: str = 'put'        # Положил квант
    RES: str = 'res'        # Зарезервировал квант
    UNR: str = 'unr'        # Разрезервировал квант


class SuggestType(str, enum.Enum):
    IN_QUANTITY: str = 'in_quantity'  # Саджест ввода количества (те на экране нужно ввести какуюто цифру)
    IN_PACKAGE: str = 'in_package'    # саджест ввода/сканирования идентификатора упаковки
    IN_LOCATION: str = 'in_location'  # саджест ввода/сканирования местоположения(location)
    IN_RESOURCE: str = 'in_resource'  # сканирование ресурса
    IN_VALID: str = 'in_valid'        # ввод даны истечения срока годности, когда просто ввод а не создание партии
    NEW_PACKAGE: str = 'new_package'  # саджест создания новой package
    NEW_LOT: str = 'new_lot'          # саджест создания партии / не путать с in_valid


class SuggestStatus(str, enum.Enum):
    WAITING: str = 'waiting'  # Ожидает подверждения
    DONE: str = 'done'        # Выполнен


class Suggest(Base, AllMixin):
    """
    Suggest Саджест, это набор минимальных действий для  [[Move]] выполнив который Move будет выполнен, например
    """
    __tablename__ = "suggest"
    lsn_seq = Sequence(f'suggest_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    move_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('move.id', ondelete='CASCADE'), index=True)
    priority: Mapped[int]
    type: Mapped[SuggestType]
    value: Mapped[Optional[str]]    # это значение которое или нужно заполнить или уже заполненное и нужно подвердить
    user_done_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)

class MoveLog(Base, AllMixin):
    """
    MoveLog - это любое изменение остатка товаров как с точки зрения резервирования остатка, так и с точки зрения прибытия/выбития
    MoveLog создается при действиях Move, когда обьект изменяет расчет
    Например:
    Если создается Move на 10 товаров A, и в момент смены статуса на confirmed создается движеление MoveLog с типом reserve на 10 пирожков,
    при условии, что все эти пирожки были доступны для резерва, и установися статус confirmed в обьекте Move
    Если было доступно только 5, то создасться MoveLog движение на 5 пирожков, при этом статус документа Move будет partially
    Когда же Move попытается сменить статус На Done - обсалютно ВСЕ документы по нему сторнируются (создаются движения с обратным знаком) и
    Создаются движения с типом get - на ячейке источнике и put на ячейке назначения
    ВАЖНО: на ячейка с типом external движения не создаются TODO: правда ли не надо?

    TODO: Нужно ли делать MoveLog при перемещении package???? кажется что только при выбытии/прибытии упаковки на склад

    """
    __tablename__ = "move_log"
    lsn_seq = Sequence(f'move_log_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)  # ForeignKey("basic.product.id")
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)  # ForeignKey("basic.store.id")
    location_class: Mapped[LocationClass] = mapped_column(index=True)
    location_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('location_type.id', ondelete='SET NULL'), index=True)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"), index=True)
    lot_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"), index=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    quantity: Mapped[float]
    reserved_quantity: Mapped[float]

