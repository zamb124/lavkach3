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
    backorder_order_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("order.id", ondelete='SET NULL'))# Тип Ордера возврата разницы
    backorder_action_type: Mapped[BackOrderAction] = mapped_column(default=BackOrderAction.ASK)                 # Поведение возврата разницы
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)                                     # Склад
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)                                   # Партнер (если у опредленного партнера своя стратегия)
    reservation_method: Mapped[ReservationMethod] = mapped_column(default=ReservationMethod.AT_CONFIRM)         # Метод резервирование
    reservation_time_before: Mapped[Optional[int]] = mapped_column(default=0)                                   # Минуты до начала резервирования
    allowed_package_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)            # Разрешенные типы упаковок
    exclusive_package_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)          # Исключение типы упаковок
    homogeneity: Mapped[bool]                                                                                   # Признак Гомогенности
    allow_create_package: Mapped[bool]                                                                          # Можно ли создавать упаковки
    can_create_order_manualy: Mapped[bool]                                                                      # Можно ли создавать Ордер вручную
    overdelivery: Mapped[bool]                                                                                  # Возможно ли Overdelivery
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
        UniqueConstraint('external_id', 'company_id', name='_order_companyid_external_id_uc'),
    )
    lsn_seq = Sequence(f'order_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("order.id", ondelete="CASCADE"))
    external_id: Mapped[Optional[str]]
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)
    lot_id: Mapped[Optional['Lot']] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"))
    origin_type: Mapped[Optional[str]] = mapped_column(index=True)
    origin_number: Mapped[Optional[str]] = mapped_column(index=True)
    planned_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    actual_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    edited_by: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    expiration_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    users_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)
    description: Mapped[Optional[str]]
    status: Mapped[OrderStatus]
    moves: Mapped[list["Move"]] = relationship(back_populates="order", )


class MoveStatus(str, Enum):
    DRAFT:      str = 'draft'
    WAITING:    str = 'waiting'
    CONFIRMED:  str = 'confirmed'
    PARTIALY:   str = 'partially'
    ASSIGNED:   str = 'assigned'
    DONE:       str = 'done'
    CANCELED:   str = 'canceled'


class Move(Base, AllMixin):
    """
    Move - это часть Order, но определяющее уже конкретную позицию товара
    """
    __tablename__ = "move"
    lsn_seq = Sequence(f'move_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("move.id", ondelete='RESTRICT'))
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('order.id', ondelete='RESTRICT'))
    order: Mapped['Order'] = relationship(back_populates="moves",)
    location_src_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    location_dest_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    lot_id: Mapped[Optional['Lot']] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"))

    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    quantity: Mapped[float]
    reserved_quantity: Mapped[float]
    expiration_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    uom_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("uom.id", ondelete="RESTRICT"), index=True)
    status: Mapped[MoveStatus]


class MoveLogType(str, Enum):
    GET: str = 'get'        # Взял квант
    PUT: str = 'put'        # Положил квант
    RES: str = 'res'        # Зарезервировал квант
    UNR: str = 'unr'        # Разрезервировал квант


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

