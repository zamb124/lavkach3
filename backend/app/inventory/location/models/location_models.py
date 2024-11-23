import uuid
from typing import Optional

from sqlalchemy import Sequence, Uuid, ForeignKey, text, JSON, select
from sqlalchemy.orm import mapped_column, Mapped, relationship, column_property

from app.inventory.location.enums import LocationClass, PutawayStrategy, BlockerEnum
from app.inventory.mixins import LocationMixin
from core.db import Base
from core.db.mixins import AllMixin
from core.db.types import ids


class LocationType(Base, AllMixin, LocationMixin):
    """
    Типы местоположения - Обозначают набор свойств местоположения, например Паллет, или ячейка, или ящик, или зона.

    Атрибуты:
        title (str): Название типа местоположения.
        store_id (Optional[uuid.UUID]): Идентификатор магазина.
        allowed_package_type_ids (Optional[ids]): Разрешенные типы упаковок.
        exclude_package_type_ids (Optional[ids]): Исключенные типы упаковок.
        is_homogeneity (Optional[bool]): Запрет на 1KU 2х разных партий.
        strategy (Optional[PutawayStrategy]): Стратегия комплектования.
        is_can_negative (Optional[bool]): Может иметь отрицательный остаток.
        capacity (Optional[dict]): Вместимость.
    """
    __tablename__ = "location_type"
    lsn_seq = Sequence(f'location_type_lsn_seq')
    title: Mapped[str] = mapped_column(index=True)
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    allowed_package_type_ids: Mapped[Optional[ids]] = mapped_column(index=True)  # Разрешенные типы упаковок
    exclude_package_type_ids: Mapped[Optional[ids]] = mapped_column(index=True)  # Исключение типы упаковок
    is_homogeneity: Mapped[Optional[bool]] = mapped_column(default=False, index=True)  # Запрет на 1KU 2х разных партий
    strategy: Mapped[Optional['PutawayStrategy']] = mapped_column(default=PutawayStrategy.FEFO)  # Стратегия комплектования
    is_can_negative: Mapped[Optional[bool]] = mapped_column(server_default=text('false'), index=True)  # Может иметь отрицательный остаток
    capacity: Mapped[Optional[dict]] = mapped_column(JSON)  # Вместимость
    storage_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('storage_type.id'), index=True)


class Location(Base, AllMixin):
    """
    **Местоположение** - это объект, хранящий в себе кванты, а также другие локации.
    Атрибуты:
        title (str): Название местоположения/или идентификатор.
        store_id (uuid.UUID): Идентификатор магазина.
        location_class (LocationClass): Класс местоположения.
        location_type_id (uuid.UUID): Идентификатор типа местоположения.
        location_type_rel (Optional[LocationType]): Связь с типом местоположения.
        location_id (Optional[uuid.UUID]): Идентификатор родительского местоположения.
        zone_id (Optional[uuid.UUID]): Идентификатор зоны.
        is_active (Optional[bool]): Активность местоположения.
        block (BlockerEnum): Статус блокир��вки местоположения.
    """
    __tablename__ = "location"
    lsn_seq = Sequence(f'location_lsn_seq')
    title: Mapped[str] = mapped_column(index=True)
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    location_class: Mapped[LocationClass] = mapped_column(index=True)
    location_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('location_type.id'), index=True)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id"), index=True)
    location_type_rel: Mapped[Optional[LocationType]] = relationship(lazy="noload")
    is_active: Mapped[Optional[bool]] = mapped_column(default=True)
    block: Mapped[BlockerEnum] = mapped_column(default=BlockerEnum.FREE, index=True)