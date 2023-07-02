import uuid
from enum import Enum

from sqlalchemy import Column, Unicode, BigInteger, ForeignKey, Sequence
from sqlalchemy import Numeric, Uuid
from sqlalchemy.orm import relationship

from core.db import Base
from core.db.mixins import AllMixin


class UomType(str, Enum):
    SMALLER: str = 'smaller'
    STANDART: str = 'standart'
    BIGGER: str = 'bigger'


class Uom(Base, AllMixin):
    __tablename__ = "uom"

    lsn_seq = Sequence(f'uom_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    category_id = Column(Uuid, ForeignKey("uom_category.id"), nullable=True)
    category = relationship("UomCategory", back_populates='uoms', lazy='selectin')
    type = Column(Unicode(30), nullable=False, index=True, default=UomType.STANDART)
    ratio = Column(Numeric(12, 2), default=1)
    precision = Column(Numeric(12, 2), default=0.01)
