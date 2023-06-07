from sqlalchemy import Column, DateTime, func, UUID, BigInteger, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declared_attr
import uuid


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )

class CompanyMixin:
    @declared_attr
    def company_id(cls): #company_id = Column(UUID, ForeignKey("companies.id"))
        return Column(
            UUID,
            ForeignKey("companies.id"),
            index=True
        )

class LsnMixin:
    @declared_attr
    def lsn_seq(cls):
        return Sequence(
            f'{cls.__tablename__}_lsn_seq'
        )
    @declared_attr
    def lsn(cls):
        return Column(
            BigInteger,
            index=True,
            server_onupdate=getattr(cls, 'lsn_seq').next_value(),
        )