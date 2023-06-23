from sqlalchemy import Column, Unicode, BigInteger, Boolean, Uuid, ForeignKey, Sequence
from sqlalchemy_utils.types import PasswordType, EmailType, CountryType, ChoiceType, JSONType, LocaleType, PhoneNumber, PhoneNumberType
from sqlalchemy_utils import CurrencyType, Currency, CountryType, LocaleType
from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin
import uuid
from enum import Enum
from sqlalchemy.orm import relationship

class PartnerType(str, Enum):
    PARTNER: str = 'partner' # Просто партнер у которого можно закупать или продавать
    CONTACT: str = 'contact' # Контакт типа просто субкарточка с контактами
    SUBPARTNER: str = 'subpartner' # Субпартнер аля контакт, но как бы у него тоже можно покупать и продавать
    INTERCOMPANY: str = 'intercompany' # Это другое подразделение своей же компании
    STORE: str = 'store' # Карточка для стора
    USER: str = 'user' # Карточка для юзера, для того, что бы у Юзера тоже можно было что то покупать тк любой сотрудник компании это тоже партнер

class Partner(Base, TimestampMixin):
    __tablename__ = "partner"
    lsn_seq = Sequence(f'partner_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid(as_uuid=False), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    #
    type = Column(Unicode(30), nullable=False, default=PartnerType.PARTNER)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    parent_id = Column(Uuid, ForeignKey("partner.id"), index=True, nullable=True)
    parent = relationship("Partner", lazy='selectin')
    phone_number = Column(PhoneNumberType(), nullable=True)
    email = Column(EmailType, nullable=True)
    country = Column(CountryType, default='US')
    #
    created_user_id = Column(Uuid, ForeignKey("user.id"), index=True, nullable=False)
    locale = Column(LocaleType, default='en_US')
    currency = Column(CurrencyType, nullable=False, default='USD')
    #
    #bank_id
    #bank_account_id