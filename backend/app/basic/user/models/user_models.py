import uuid
from enum import Enum

from fastapi_localization import lazy_gettext as _
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode, Boolean, Uuid, Sequence
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import PasswordType, EmailType, CountryType, LocaleType, PhoneNumberType

from core.db import Base
from core.db.mixins import TimestampMixin, VarsMixin, LsnMixin


class UserType(str, Enum):
    COMMON: str = _('Common User')
    STORE: str = _('Store User')
    COURIER: str = _('Courier')


class User(Base, TimestampMixin, VarsMixin, LsnMixin):
    __tablename__ = "user"
    __table_args__ = (UniqueConstraint('email', 'companies', name='_user_company_id_uc'),)

    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    lsn_seq = Sequence(f'user_lsn_seq')
    # lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    password = Column(PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],
        deprecated=['md5_crypt']
    ))
    email = Column(EmailType, nullable=False, unique=True)
    country = Column(CountryType, default='RU')
    locale = Column(LocaleType, default='en_US')
    phone_number = Column(PhoneNumberType())
    nickname = Column(Unicode(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    type = Column(Unicode(255), nullable=False, default=UserType.COMMON)
    store_id = Column(Uuid, ForeignKey("store.id"), index=True, nullable=True)
    store = relationship("Store", back_populates='store_users', lazy='selectin')
    companies = Column(ARRAY(Uuid), index=True, nullable=True)
    roles = Column(ARRAY(Uuid), index=True, nullable=True, default=[])
