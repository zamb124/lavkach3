import uuid

from sqlalchemy import Uuid, Sequence, Enum, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app.bus.bus.enums import BusStatus
from core.db import Base
from core.db.mixins import AllMixin
from core.helpers.cache import CacheTag


class Bus(Base, AllMixin):
    __tablename__ = "bus"
    lsn_seq = Sequence(f'bus_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    cache_tag: Mapped[CacheTag] = mapped_column(index=True)
    message: Mapped[str]
    status: Mapped[BusStatus] = mapped_column(index=True)
