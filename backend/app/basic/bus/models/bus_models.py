import uuid

from sqlalchemy import Uuid, Sequence
from sqlalchemy.orm import mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin
from core.helpers.cache import CacheTag


class Bus(Base, AllMixin):
    __tablename__ = "bus"
    lsn_seq = Sequence(f'bus_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    cache_tag: Mapped[CacheTag]
    message: Mapped[str]
