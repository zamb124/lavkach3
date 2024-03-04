import enum
import uuid
from enum import Enum
from typing import Optional
import datetime
from sqlalchemy import Column, Unicode, Sequence, Uuid, ForeignKey, DateTime, func, text, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql.sqltypes import ARRAY

from core.db import Base
from core.db.mixins import AllMixin


class LocationClass(enum.Enum):
    """
    **Классификация** типов местоположения, обозначающий свойства типов местоположения
    - partner - Зона внешняя (например поставщика товаров)
    - place - Статичный класс местоположения в пространстве, например ячейка на складе или магазине
    - zone - Зона, которая отвечает за агрегацию свойств местоположений, например стратегия приемки или отгрузки
    - resource - Статически/динамическое местоположение означающее ресурс с помощью которого происзодит перемещение, например Тележка, или штабелер или что то иное
    - package - Динамическое местоположение, например паллета коробка
    - lost - класс типа местоположения отвечающий аккумулирование расхождений в рамках набора локаций, может быть ограничен зоной, магазином или компанией
    - inventory - класс типов ячеек, которы аккумулирует расхождения при легальной инвентаризации
    - scrap - класс хранение некондиционного товара
    - buffer - класс типов ячеек отвечающий за буфер приемки например за зону приемки или зону отгрузки
    -
    """
    partner = "partner"
    place = "place"
    resource = "resource"
    package = "package"
    zone = "zone"
    lost = "lost"
    inventory = "inventory"
    scrap = "scrap"


class LocationType(Base, AllMixin):
    """
    **Типы местоположения** -  Обозначают набор свойств местоположения, например Паллет, или ячейка, или ящик, или зона
    """
    __tablename__ = "location_type"
    lsn_seq = Sequence(f'location_type_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str]
    location_class = Mapped[LocationClass]


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
    store_id: Mapped[Uuid] = mapped_column(Uuid, index=True)
    parent_id: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("location.id"), index=True)
    active: Mapped[bool] = mapped_column(default=True)
    location_type_id: Mapped[Uuid] = mapped_column(ForeignKey('location_type.id'), index=True)
    product_storage_type_ids: Mapped[Optional[list[str]]] = mapped_column(type_=ARRAY(String), index=True, nullable=True)
    partner_id: Mapped[Optional[Uuid]] = mapped_column(Uuid, index=True, nullable=True)
