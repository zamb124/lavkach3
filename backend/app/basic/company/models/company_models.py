import uuid

from sqlalchemy import Column, Unicode, BigInteger, Uuid, Sequence
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy_utils import CurrencyType, CountryType, LocaleType

from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin


class Company(Base, TimestampMixin, LsnMixin):
    __tablename__ = "company"
    lsn_seq = Sequence(f'company_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False, index=True)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    country = Column(CountryType, default='US')
    locale = Column(LocaleType, default='en_US')
    currency = Column(CurrencyType, nullable=False, default="USD")
    stores = relationship("Store", lazy='selectin', back_populates="company")
