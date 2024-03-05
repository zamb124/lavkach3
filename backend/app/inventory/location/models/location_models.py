import uuid
from enum import Enum
from typing import Optional
import datetime
from sqlalchemy import Column, Unicode, Sequence, Uuid, ForeignKey, DateTime, func, text, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql.sqltypes import ARRAY

from core.db import Base
from core.db.mixins import AllMixin
from app.inventory.location.enums import LocationClass, PutawayStrategy




class LocationType(Base, AllMixin):
    """
    **Типы местоположения** -  Обозначают набор свойств местоположения, например Паллет, или ячейка, или ящик, или зона
    """
    __tablename__ = "location_type"
    lsn_seq = Sequence(f'location_type_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str]
    location_class: Mapped[LocationClass]



class Location(Base, AllMixin):
    """
    **Местоположение** -  это обьект хранящий в себе кванты, а так же другие локации
    Местоположение может быть статичная или динамическая определяется типом:
    - shelve - статичная ячейка хранения в магазине
    - rack - статичная стеллаж
    - package - динамический тип местоположение, например Паллет
    """
    __tablename__ = "location"
    lsn_seq = Sequence(f'location_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str]
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id"), index=True)
    active: Mapped[Optional[bool]] = mapped_column(default=True)
    location_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('location_type.id'), index=True)
    product_storage_type_ids: Mapped[Optional[list[str]]] = mapped_column(type_=ARRAY(String), index=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)
    homogeneity: Mapped[Optional[bool]] = mapped_column(default=False)
    allow_create_package: Mapped[Optional[bool]] = mapped_column(default=True)                                   # Можно ли создавать упаковки# Признак Гомогенности
    allowed_package_ids: Mapped[Optional[list['Location']]] = mapped_column(ARRAY(Uuid), index=True)             # Разрешенные типы упаковок
    exclusive_package_ids: Mapped[Optional[list['Location']]] = mapped_column(ARRAY(Uuid), index=True)           # Исключение типы упаковок
    allowed_order_types_ids: Mapped[Optional[list['OrderType']]] = mapped_column(ARRAY(Uuid), index=True)        # Разрешенные типы упаковок
    exclusive_order_types_ids: Mapped[Optional[list['OrderType']]] = mapped_column(ARRAY(Uuid), index=True)      # Разрешенные типы упаковок
    strategy: Mapped[Optional['PutawayStrategy']] = mapped_column(default=PutawayStrategy.FEFO)                  # Стратегия комплектования
