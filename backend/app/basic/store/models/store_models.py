import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import Sequence, Uuid
from sqlalchemy.orm import mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin


class StoreType(str, Enum):
    INTERNAL: str = 'internal'
    WMS: str = 'wms'


class Store(Base, AllMixin):
    __tablename__ = "store"
    lsn_seq = Sequence(f'store_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    external_number: Mapped[Optional[str]] = mapped_column(unique=True)
    address: Mapped[str]
    source: Mapped[str] = mapped_column(default=StoreType.INTERNAL)


