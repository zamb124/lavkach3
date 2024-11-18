import uuid
from typing import Optional

from sqlalchemy import Uuid, Sequence
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy_utils import CurrencyType, CountryType, LocaleType

from .....db import Base
from .....db.mixins import TimestampMixin, LsnMixin


class Company(Base, TimestampMixin, LsnMixin):
    __tablename__ = "company"
    lsn_seq = Sequence(f'company_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    external_number: Mapped[Optional[str]] = mapped_column(unique=True)
    country: Mapped[str] = mapped_column(CountryType, default='US')
    locale: Mapped[str] = mapped_column(LocaleType, default='en_US')
    currency: Mapped[str] = mapped_column(CurrencyType, default="USD")
    #user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id"), index=True)
