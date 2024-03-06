import uuid
from enum import Enum
from typing import Optional

from fastapi_localization import lazy_gettext as _
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode, Boolean, Uuid, Sequence
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils.types import PasswordType, EmailType, CountryType, LocaleType, PhoneNumberType

from core.db import Base
from core.db.mixins import TimestampMixin, VarsMixin, LsnMixin


class UserType(str, Enum):
    COMMON: str = _('Common User')
    STORE: str = _('Store User')
    COURIER: str = _('Courier')


class User(Base, TimestampMixin, VarsMixin, LsnMixin):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint('email', 'companies', name='_user_company_id_uc'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    external_id: Mapped[Optional[str]]
    lsn_seq = Sequence(f'user_lsn_seq')
    # lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    password: Mapped[str] = mapped_column(PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],
        deprecated=['md5_crypt']
    ))
    email: Mapped[Optional[str]] = mapped_column(EmailType)
    country: Mapped[str] = mapped_column(CountryType, default='US')
    locale: Mapped[str] = mapped_column(LocaleType, default='en_US')
    phone_number: Mapped[Optional[str]] = mapped_column(PhoneNumberType)
    nickname: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)
    type: Mapped[str] = mapped_column(default=UserType.COMMON)
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("store.id"), index=True)
    store: Mapped['Store'] = relationship(back_populates='store_users', lazy='selectin')
    companies: Mapped[Optional[uuid.UUID]] = mapped_column(ARRAY(Uuid), index=True)
    roles: Mapped[Optional[uuid.UUID]] = mapped_column(ARRAY(Uuid), index=True, default=[])