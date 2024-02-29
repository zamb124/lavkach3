from sqlalchemy import Column, Unicode, BigInteger, Boolean, ForeignKey, Sequence, Enum, Text, Integer, DECIMAL, \
    Numeric, Uuid
from sqlalchemy import Column, Unicode, BigInteger, Boolean, ForeignKey, Sequence
from sqlalchemy_utils import CurrencyType, Currency, CountryType, LocaleType
from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin, CompanyMixin, AllMixin
import uuid
from enum import Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped


class UomCategory(Base, AllMixin):
    __tablename__ = "uom_category"
    lsn_seq = Sequence(f'uom_category_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    uoms = relationship("Uom", back_populates='category', lazy='selectin')
