import uuid
from enum import Enum

from sqlalchemy import Column, Unicode, Sequence, Uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin


class StoreType(str, Enum):
    INTERNAL: str = 'internal'
    WMS: str = 'wms'


class Store(Base, AllMixin):
    __tablename__ = "store"
    lsn_seq = Sequence(f'store_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    address = Column(Unicode(255), nullable=False)
    source = Column(Unicode(20), nullable=False, default=StoreType.INTERNAL)
    store_users = relationship("User", lazy='selectin')
    company = relationship("Company", lazy='immediate', back_populates="stores")
