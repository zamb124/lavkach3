import enum
import uuid
from enum import Enum
from typing import Optional
import datetime
from sqlalchemy import Column, Unicode, Sequence, Uuid, ForeignKey, DateTime, func, text
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin
'

class LocationClass(enum.Enum):
    """
    **Классификация** типов местоположения, обозначающий свойства типов местоположения
    - place - Статичный класс местоположения в пространстве, например ячейка на складе или магазине
    - package - Динамическое местоположение, например паллета или тележка
    - zone - Зона, которая отвечает за агрегацию свойств местоположений, например стратегия приемки или отгрузки
    - lost - класс типа местоположения отвечающий аккумулирование расхождений в рамках набора локаций, может быть ограничен зоной, магазином или компанией
    - inventory - класс типов ячеек, которы аккумулирует расхождения при легальной инвентаризации
    - scrap - класс хранение некондиционного товара
    - buffer - класс типов ячеек отвечающий за буфер приемки например за зону приемки или зону отгрузки
    """
    place = "place"
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
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
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
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str]
    store_id: Mapped[Uuid] = mapped_column(ForeignKey("store.id", ondelete="CASCADE"))
    parent_id: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("location.id"), index=True)
    parent = relationship("Location", lazy='selectin')
    active: Mapped[bool] = mapped_column(default=True)
    type:


    product_id: Mapped[Uuid] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"))
    store_id: Mapped[Uuid] = mapped_column(ForeignKey("store.id", ondelete="CASCADE"))
    location_id: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("location.id", ondelete="CASCADE"))
    lot_id: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("lot.id", ondelete="CASCADE"))
    owner_id: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("owner.id", ondelete="CASCADE"))
    quantity: Mapped[float]
    reserved_quantity: Mapped[float]
    expiration_date = Column(DateTime(timezone=True))
    uom_id: Mapped[Uuid] = mapped_column(ForeignKey("uom.id", ondelete="CASCADE"), index=True)
