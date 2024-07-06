import datetime
import uuid
from typing import Optional

from sqlalchemy import Sequence, Uuid, DateTime, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from app.inventory.mixins import StockMixin
from core.db import Base
from core.db.mixins import AllMixin
from core.db.types import ids


class Lot(Base, AllMixin):
    """
    **Партия** -  Партия обозначает уникальный набор аттрибутов конкретного количества товаров, например Единый срок годности
    или пришедшая от другого поставщика
    """
    __tablename__ = "lot"
    __table_args__ = (UniqueConstraint('external_number', 'product_id', 'partner_id', name='_lot_ex_pr_par_id_uc'),)
    lsn_seq = Sequence(f'lot_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    expiration_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=True)
    external_number: Mapped[Optional[str]] = mapped_column(nullable=False, unique=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)


class Quant(Base, AllMixin, StockMixin):
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
        'store_id', 'location_id', 'lot_id', 'expiration_datetime', name='_quant_st_loc_lot_ex_id_uc'
    ),)
    lsn_seq = Sequence(f'quant_lsn_seq')
    quantity: Mapped[float]
    reserved_quantity: Mapped[float]
    incoming_quantity: Mapped[float]
    expiration_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    uom_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)
    move_ids: Mapped[Optional[ids]] = mapped_column(index=True)

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity
