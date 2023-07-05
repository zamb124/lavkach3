import uuid

from sqlalchemy import Column, Unicode, BigInteger, Uuid, Sequence, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import CurrencyType, CountryType, LocaleType

from core.db import Base
from core.db.mixins import TimestampMixin, AllMixin


class ChannelType(str, Enum):
    GROUP = 'group'
    USER = 'user'
    COMPANY = 'company'


class Channel(AllMixin):
    __tablename__ = "channel"
    lsn_seq = Sequence(f'channel_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False, index=True)


class Bus(Base, AllMixin):
    __tablename__ = "bus"
    lsn_seq = Sequence(f'bus_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    channel_id = Column(Uuid, ForeignKey("channel.id"), nullable=True)
    title = Column(Unicode(255), nullable=False, index=True)
