import uuid

from sqlalchemy import Uuid, Sequence, Enum, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped


from core.db import Base
from core.db.mixins import AllMixin


class ChannelType(str, Enum):
    GROUP = 'group'
    USER = 'user'
    COMPANY = 'company'


class Channel(AllMixin):
    __tablename__ = "channel"
    lsn_seq = Sequence(f'channel_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str]


class Bus(Base, AllMixin):
    __tablename__ = "bus"
    lsn_seq = Sequence(f'bus_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    channel_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("channel.id"), nullable=True)
    title: Mapped[str]
