import uuid

from sqlalchemy import Uuid, Sequence
from sqlalchemy.orm import mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin
from core.helpers.cache import CacheTag
from ...bus.enums import BusStatus


class Bus(Base, AllMixin):
    __tablename__ = "bus"
    lsn_seq = Sequence(f'bus_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    cache_tag: Mapped[CacheTag] = mapped_column(index=True)
    message: Mapped[str]
    status: Mapped[BusStatus] = mapped_column(index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=True)