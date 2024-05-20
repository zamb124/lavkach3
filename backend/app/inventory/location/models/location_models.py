import uuid
from typing import Optional

from sqlalchemy import Sequence, Uuid, ForeignKey, String, text
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql.sqltypes import ARRAY

from app.inventory.location.enums import LocationClass, PutawayStrategy
from core.db import Base
from core.db.mixins import AllMixin
from core.db.types import ids


class LocationType(Base, AllMixin):
    """
    **Типы местоположения** -  Обозначают набор свойств местоположения, например Паллет, или ячейка, или ящик, или зона
    """
    __tablename__ = "location_type"
    lsn_seq = Sequence(f'location_type_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str]
    location_class: Mapped[LocationClass]
    is_homogeneity: Mapped[Optional[bool]] = mapped_column(default=False)  # Запрет на 1KU 2х разных партий
    allowed_package_ids: Mapped[Optional[ids]] = mapped_column(index=True)  # Разрешенные типы упаковок
    exclude_package_ids: Mapped[Optional[ids]] = mapped_column(index=True)  # Исключение типы упаковок
    strategy: Mapped[Optional['PutawayStrategy']] = mapped_column(default=PutawayStrategy.FEFO)  # Стратегия комплектования
    is_can_negative: Mapped[Optional[bool]] = mapped_column(server_default=text('false')) # Может иметь отрицательный остаток


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
    location_class: Mapped[LocationClass] = mapped_column(index=True)
    title: Mapped[str]
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id"), index=True)
    is_active: Mapped[Optional[bool]] = mapped_column(default=True)
    location_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('location_type.id'), index=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)  # Кому принадлежит товар
