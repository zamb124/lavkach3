from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey, Sequence

from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin
import uuid


class Company(Base, TimestampMixin):
    __tablename__ = "companies"
    lsn_seq = Sequence(f'companies_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value())
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    lang = Column(Unicode(255), nullable=False)
    country = Column(Unicode(255), nullable=False)
    currency = Column(Unicode(255), nullable=False)
