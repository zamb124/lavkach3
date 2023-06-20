from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey, Sequence, Enum, Text, Integer, DECIMAL, Numeric
from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey, Sequence
from sqlalchemy_utils import CurrencyType, Currency, CountryType, LocaleType
from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin, CompanyMixin, AllMixin
import uuid
from enum import Enum
from sqlalchemy.orm import relationship

class UomCategory(Base, AllMixin):
    __tablename__ = "uom_category"
    __allow_unmapped__ = True
    lsn_seq = Sequence(f'uom_category_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)

class UomType(str, Enum):
    SMALLER: str = 'smaller'
    STANDART: str = 'standart'
    BIGGER: str = 'bigger'

class Uom(Base, AllMixin):
    __tablename__ = "uom"
    __allow_unmapped__ = True

    lsn_seq = Sequence(f'uom_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)

    type = Column(Unicode(30), nullable=False, index=True, default=UomType.STANDART)
    ratio = Column(Numeric(12, 2), default=1)
    precision = Column(Numeric(12, 2), default=0.01)