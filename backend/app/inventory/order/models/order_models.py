import datetime
import enum
import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import Sequence, Uuid, ForeignKey, DateTime, UniqueConstraint, ARRAY, \
    String
from sqlalchemy.orm import relationship, mapped_column, Mapped

# from app.inventory.location.models import Location, LocationClass
from app.inventory.location.enums import LocationClass, PutawayStrategy
from app.inventory.location.models import Location
from app.inventory.order.enums.order_enum import MoveStatus, OrderClass, BackOrderAction, ReservationMethod, \
    OrderStatus, MoveType, SuggestType
from app.inventory.quant.models import Lot, Quant
from core.db import Base
from core.db.mixins import AllMixin, CreatedEdited
from core.db.types import ids



class OrderType(Base, AllMixin, CreatedEdited):
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
    allowed_location_src_ids: Mapped[ids] = mapped_column(index=True)      # Разрешенные зоны для подбора
    exclude_location_src_ids: Mapped[ids] = mapped_column(index=True)    # Искличенные зоны из подбора
    allowed_location_dest_ids: Mapped[ids] = mapped_column(index=True)     # Разрешенные зона для назначения
    exclude_location_dest_ids: Mapped[ids] = mapped_column(index=True)    # Исключение зон из назначения
    allowed_location_type_src_ids: Mapped[ids] = mapped_column(index=True)      # Разрешенные типы зоны для подбора
    exclude_location_type_src_ids: Mapped[ids] = mapped_column(index=True)     # Искличенные типы зоны из подбора
    allowed_location_type_dest_ids: Mapped[ids] = mapped_column(index=True)        # Разрешенные типы зоны для назначения
    exclude_location_type_dest_ids: Mapped[ids] = mapped_column(index=True)     # Искличенные типы зоны для назначения
    allowed_location_class_src_ids: Mapped[Optional[ids]] = mapped_column(ARRAY(String), server_default='{}',index=True)                 # Разрешенные классы зона для подбора
    exclude_location_class_src_ids: Mapped[Optional[ids]] = mapped_column(ARRAY(String), server_default='{}', index=True)               # Исключение классы зон для подбора
    allowed_location_class_dest_ids: Mapped[Optional[ids]] = mapped_column(ARRAY(String), server_default='{}', index=True)                 # Разрешенные классы зона для назначения
    exclude_location_class_dest_ids: Mapped[Optional[ids]] = mapped_column(ARRAY(String), server_default='{}', index=True)               # Исключение классы зон для назначения
    order_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("order_type.id", ondelete='CASCADE'))# Тип Ордера возврата разницы
    backorder_action_type: Mapped[BackOrderAction] = mapped_column(default=BackOrderAction.ASK)                 # Поведение возврата разницы
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)                                     # Склад
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)                                   # Партнер (если у опредленного партнера своя стратегия)
    reservation_method: Mapped[ReservationMethod] = mapped_column(default=ReservationMethod.AT_CONFIRM)         # Метод резервирование
    reservation_time_before: Mapped[Optional[int]] = mapped_column(default=0)                                   # Минуты до начала резервирования
    allowed_package_ids: Mapped[Optional[ids]] = mapped_column(index=True)            # Разрешенные типы упаковок
    exclude_package_ids: Mapped[Optional[ids]] = mapped_column(index=True)          # Исключение типы упаковок
    is_homogeneity: Mapped[bool]                                                                                   # Признак Гомогенности
    is_allow_create_package: Mapped[bool]                                                                          # Можно ли создавать упаковки
    is_can_create_order_manualy: Mapped[bool]                                                                      # Можно ли создавать Ордер вручную
    is_overdelivery: Mapped[bool]                                                                                  # Возможно ли Overdelivery
    barcode: Mapped[str]                                                                                        # Штрих-код ордера для быстрого доступа
    strategy: Mapped['PutawayStrategy'] = mapped_column(default=PutawayStrategy.FEFO)                           # Стратегия комплектования



class Order(Base, AllMixin, CreatedEdited):
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
    planned_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    actual_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    expiration_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    user_ids: Mapped[Optional[ids]] = mapped_column(index=True)
    description: Mapped[Optional[str]]
    status: Mapped['OrderStatus'] = mapped_column(default=OrderStatus.DRAFT)
    move_list_rel: Mapped[Optional[list["Move"]]] = relationship(back_populates="order_rel", lazy="selectin")

    def __init__(self, **kwargs):
        """
            Разрешает экстра поля, но удаляет, если их нет в табличке
        """
        allowed_args = self.__mapper__.class_manager  # returns a dict
        kwargs = {k: v for k, v in kwargs.items() if k in allowed_args}
        super().__init__(**kwargs)




class Move(Base, AllMixin, CreatedEdited):
    """
    Move - это часть Order, но определяющее уже конкретную позицию товара
    """
    __tablename__ = "move"
    lsn_seq = Sequence(f'move_lsn_seq')
    type: Mapped[MoveType]
    move_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("move.id", ondelete='RESTRICT'))
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    order_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('order_type.id', ondelete='RESTRICT'), nullable=True)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('order.id', ondelete='RESTRICT'), nullable=True)
    order_rel: Mapped[Order] = relationship(back_populates='move_list_rel')
    location_src_id: Mapped[Optional[Location]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    location_dest_id: Mapped[Optional[Location]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    lot_id: Mapped[Optional['Lot']] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"))
    location_id: Mapped[Optional[Location]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    # ONE OF Возможно либо location_id либо product_id
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    quantity: Mapped[float]     # Если перемещение кпаковки, то всегда 0
    uom_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=False) # Если перемещение упаковкой то None
    quant_src_id: Mapped[Optional['Quant']] = mapped_column(ForeignKey("quant.id", ondelete="SET NULL"), index=True)
    quant_dest_id: Mapped[Optional['Quant']] = mapped_column(ForeignKey("quant.id", ondelete="SET NULL"), index=True)
    status: Mapped[MoveStatus] = mapped_column(default=MoveStatus.CREATED)
    suggest_list_rel: Mapped[Optional[list["Suggest"]]] = relationship(lazy="selectin")



class Suggest(Base, AllMixin):
    """
    Suggest Саджест, это набор минимальных д ействий для  [[Move]] выполнив который Move будет выполнен, например
    """
    __tablename__ = "suggest"
    lsn_seq = Sequence(f'suggest_lsn_seq')
    move_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('move.id', ondelete='CASCADE'), index=True)
    priority: Mapped[int]
    type: Mapped[SuggestType]
    value: Mapped[Optional[str]]    # это значение которое или нужно заполнить или уже заполненное и нужно подвердить
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)

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
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)  # ForeignKey("basic.product.id")
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)  # ForeignKey("basic.store.id")
    location_class: Mapped[LocationClass] = mapped_column(index=True)
    location_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('location_type.id', ondelete='SET NULL'), index=True)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"), index=True)
    lot_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"), index=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    quantity: Mapped[float]
    reserved_quantity: Mapped[float]

