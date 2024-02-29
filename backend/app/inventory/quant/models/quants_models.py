import uuid
from enum import Enum
from typing import Optional
import datetime
from sqlalchemy import Column, Unicode, Sequence, Uuid, ForeignKey, DateTime, func, text, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin, guid, guid_primary_key


class StoreType(str, Enum):
    INTERNAL: str = 'internal'
    WMS: str = 'wms'


class Lot(Base, AllMixin):
    """
    **Партия** -  Партия обозначает уникальный набор аттрибутов конкретного количества товаров, например Единый срок годности
    или пришедшая от другого поставщика
    """
    __tablename__ = "lot"
    __table_args__ = (UniqueConstraint('external_id', 'product_id', 'partner_id', name='_lot_ex_pr_par_id_uc'),)
    lsn_seq = Sequence(f'lot_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    expiration_date = Column(DateTime(timezone=True))
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(nullable=False, unique=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)


class Quant(Base, AllMixin):
    """
    **Квант** -  это минимальная и уникальная единица остатка являющаяся одинаковой по своим свойствам в рамках местоположения
    Например, если в ячейку "A" на которой находится уже товар "A" с партией "A" и количеством 5 добавляется товар
    "A" с партией "A" и количеством 5, то к в ячейке "A" будет создан квант с количеством 10,
    Но если добавляется товар "A" c партией "B", то в местоположении будет создано 2 кванта
    *Поля свойства определяющие уникальность кванта*
    - store_id: ID магазина
    - location_id: ID местоположения кванта
    - lot_id: ID партии кванта
    - owner_id: ID собственника кванта
    - uom_id: Единица измерения, в которой находится квант
    quantity: Количество товара в кванте
    reserved_quantity: Зарезервирвоанное количество товара в кванте
    """
    __tablename__ = "quant"
    __table_args__ = (UniqueConstraint(
        'store_id', 'location_id', 'lot_id', 'expiration_date', name='_quant_st_loc_lot_ex_id_uc'
    ),)
    lsn_seq = Sequence(f'quant_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)                                          # ForeignKey("basic.product.id")
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)                                            # ForeignKey("basic.store.id")
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id", ondelete="SET NULL"))
    lot_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"))
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    quantity: Mapped[float]
    reserved_quantity: Mapped[float]
    expiration_date = Column(DateTime(timezone=True))
    uom_id: Mapped[Uuid] = mapped_column(ForeignKey("uom.id", ondelete="RESTRICT"), index=True)
