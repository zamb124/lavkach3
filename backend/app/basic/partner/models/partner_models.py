import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import Uuid, ForeignKey, Sequence
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy_utils import CurrencyType, CountryType, LocaleType
from sqlalchemy_utils.types import EmailType, PhoneNumberType

from core.db import Base
from core.db.mixins import AllMixin


class PartnerType(str, Enum):
    """
    PARTNER: Просто партнер у которого можно закупать или продавать
    CONTACT: Контакт типа просто субкарточка с контактами
    SUBPARTNER: Субпартнер аля контакт, но как бы у него тоже можно покупать и продавать
    INTERCOMPANY: Это другое подразделение своей же компании
    STORE: Карточка для стора
    USER:Карточка для юзера, для того, что бы у Юзера тоже можно было что то покупать тк любой сотрудник компании это тоже партнер
    """
    PARTNER: str = 'partner'
    CONTACT: str = 'contact'
    SUBPARTNER: str = 'subpartner'
    INTERCOMPANY: str = 'intercompany'
    STORE: str = 'project'
    USER: str = 'user'

class Partner(Base,AllMixin):
    __tablename__ = "partner"
    lsn_seq = Sequence(f'partner_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    #
    type: Mapped[PartnerType] = mapped_column(default=PartnerType.PARTNER)
    external_number: Mapped[Optional[str]] = mapped_column(unique=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("partner.id"), index=True)
    partner_rel: Mapped['Partner'] = relationship(lazy='selectin')
    phone_number: Mapped[Optional[str]] = mapped_column(PhoneNumberType)
    email: Mapped[Optional[str]] = mapped_column(EmailType)
    country: Mapped[str] = mapped_column(CountryType, default='US')
    #
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id"), index=True)
    locale: Mapped[str] = mapped_column(LocaleType, default='en_US')
    currency: Mapped[str] = mapped_column(CurrencyType, default='USD')
