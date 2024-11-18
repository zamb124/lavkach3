import uuid
from enum import Enum
from typing import Optional
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import Uuid, Sequence
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils.types import PasswordType, EmailType, CountryType, LocaleType, PhoneNumberType

from .....db import Base
from .....db.mixins import TimestampMixin, VarsMixin, LsnMixin
from .....db.types import ids

if TYPE_CHECKING:
    from core.core_apps.base.company.models.company_models import Company

class UserType(str, Enum):
    COMMON: str = 'Common User'
    STORE: str = 'Store User'
    COURIER: str = 'Courier'


class User(Base, TimestampMixin, VarsMixin, LsnMixin):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint('email', 'company_ids', name='_user_company_id_uc'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    external_number: Mapped[Optional[str]]
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
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("company.id"), index=True)
    company_rel: Mapped[Optional['Company']] = relationship(lazy='selectin')
    company_ids: Mapped[Optional[ids]] = mapped_column(index=True)
    role_ids: Mapped[Optional[ids]] = mapped_column(index=True)