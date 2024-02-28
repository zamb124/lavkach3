import uuid
from enum import Enum
from typing import Optional
import datetime
from sqlalchemy import Column, Unicode, Sequence, Uuid, ForeignKey, DateTime, func, text
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin


class StoreType(str, Enum):
    INTERNAL: str = 'internal'
    WMS: str = 'wms'


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
    lsn_seq = Sequence(f'quant_lsn_seq')
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    product_id: Mapped[Uuid] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"))
    store_id: Mapped[Uuid] = mapped_column(ForeignKey("store.id", ondelete="CASCADE"))
    location_id: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("location.id", ondelete="CASCADE"))
    lot_id: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("lot.id", ondelete="CASCADE"))
    owner_id: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("owner.id", ondelete="CASCADE"))
    quantity: Mapped[float]
    reserved_quantity: Mapped[float]
    expiration_date: Mapped[Optional[datetime.datetime]]
    uom_id: Mapped[Uuid] = mapped_column(ForeignKey("uom.id", ondelete="CASCADE"), index=True)
