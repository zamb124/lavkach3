from typing import Optional

from sqlalchemy import Column, Unicode, BigInteger, Boolean, Uuid, ForeignKey, Sequence
from sqlalchemy_utils.types import PasswordType, EmailType, CountryType, ChoiceType, JSONType, LocaleType, PhoneNumber, PhoneNumberType
from sqlalchemy_utils import CurrencyType, Currency, CountryType, LocaleType
from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin, AllMixin
import uuid
from enum import Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped


class PartnerType(str, Enum):
    PARTNER: str = 'partner' # Просто партнер у которого можно закупать или продавать
    CONTACT: str = 'contact' # Контакт типа просто субкарточка с контактами
    SUBPARTNER: str = 'subpartner' # Субпартнер аля контакт, но как бы у него тоже можно покупать и продавать
    INTERCOMPANY: str = 'intercompany' # Это другое подразделение своей же компании
    STORE: str = 'store' # Карточка для стора
    USER: str = 'user' # Карточка для юзера, для того, что бы у Юзера тоже можно было что то покупать тк любой сотрудник компании это тоже партнер

class Partner(Base,AllMixin):
    __tablename__ = "partner"
    lsn_seq = Sequence(f'partner_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    #
    type: Mapped[PartnerType] = mapped_column(default=PartnerType.PARTNER)
    external_id: Mapped[Optional[str]] = mapped_column(unique=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("partner.id"), index=True)
    parent: Mapped['Partner'] = relationship(lazy='selectin')
    phone_number: Mapped[Optional[str]] = mapped_column(PhoneNumberType)
    email: Mapped[Optional[str]] = mapped_column(EmailType)
    country: Mapped[str] = mapped_column(CountryType, default='US')
    #
    created_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id"), index=True)
    locale: Mapped[str] = mapped_column(LocaleType, default='en_US')
    currency: Mapped[str] = mapped_column(CurrencyType, default='USD')
