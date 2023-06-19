from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey, Sequence
from sqlalchemy_utils.types import PasswordType, EmailType, CountryType, ChoiceType, JSONType, LocaleType, PhoneNumber, PhoneNumberType
from backend.core.db import Base
from sqlalchemy.orm import RelationshipProperty, registry, relationship, composite
from backend.core.db.mixins import AllMixin
import uuid
from enum import Enum
from fastapi_localization import lazy_gettext as _

class UserType(str, Enum):
    COMMON: str = _('Common User')
    STORE: str = _('Store User')
    COURIER: str = _('Courier')

class User(Base, AllMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    lsn_seq = Sequence(f'users_lsn_seq')
    #lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
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
    nickname = Column(Unicode(255), nullable=False, unique=True)
    is_admin = Column(Boolean, default=False)
    type = Column(ChoiceType(UserType), nullable=False, default=UserType.COMMON)
    store_id = Column(UUID, ForeignKey("stores.id"), index=True, nullable=True)
    store = relationship("Store", lazy='selectin')
    company = relationship("Company", lazy='selectin')
