from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey

from core.db import Base
from core.db.mixins import TimestampMixin
import uuid


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    lang = Column(Unicode(255), nullable=False)
    country = Column(Unicode(255), nullable=False)
    currency = Column(Unicode(255), nullable=False)
