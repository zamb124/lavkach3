import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, Sequence
from sqlalchemy import Numeric, Uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.basic.product.models import Product
from core.db import Base
from core.db.mixins import AllMixin


class UomType(str, Enum):
    SMALLER: str = 'smaller'
    STANDART: str = 'standart'
    BIGGER: str = 'bigger'


class Uom(Base, AllMixin):
    __tablename__ = "uom"

    lsn_seq = Sequence(f'uom_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("uom_category.id"))
    category: Mapped['UomCategory'] = relationship(back_populates='uoms', lazy='selectin')
    products: Mapped['Product'] = relationship(back_populates='uom', lazy='selectin')
    type: Mapped[str] = mapped_column(index=True, default=UomType.STANDART)
    ratio: Mapped[float] = mapped_column(Numeric(12, 2), default=1)
    precision: Mapped[float] = mapped_column(Numeric(12, 2), default=0.01)
