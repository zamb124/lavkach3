from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey, Sequence, Enum

from backend.core.db import Base
from backend.core.db.mixins import TimestampMixin, LsnMixin, CompanyMixin, AllMixin
import uuid
from enum import Enum
from sqlalchemy.orm import relationship
class StoreType(str, Enum):
    INTERNAL: str = 'internal'
    WMS: str = 'wms'

class Store(Base, AllMixin):
    __tablename__ = "stores"
    lsn_seq = Sequence(f'stores_lsn_seq')
    #lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    address = Column(Unicode(255), nullable=False)
    source = Column(Unicode(20), nullable=False, default=StoreType.INTERNAL)
    store_users = relationship("User", lazy='selectin')
    company = relationship("Company", lazy='selectin')
