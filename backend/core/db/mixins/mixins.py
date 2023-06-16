from sqlalchemy import Column, DateTime, func, UUID, BigInteger, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils.types import  JSONType
import pytz



class VarsMixin:
    @declared_attr
    def vars(cls): #company_id = Column(UUID, ForeignKey("companies.id"))
        return Column(
            JSONType,
            nullable=True
        )

class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            default=func.now(tz=pytz.timezone('UTC')),
            nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            default=func.now(tz=pytz.timezone('UTC')),
            onupdate=func.now(tz=pytz.timezone('UTC')),
            nullable=False,
        )

class CompanyMixin:
    @declared_attr
    def company_id(cls): #company_id = Column(UUID, ForeignKey("companies.id"))
        return Column(
            UUID,
            ForeignKey("companies.id"),
            index=True,
            nullable=False
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
                getattr(cls, 'lsn_seq'),
                onupdate=getattr(cls, 'lsn_seq').next_value(), index=True
            )
class AllMixin(LsnMixin, CompanyMixin,TimestampMixin,VarsMixin):
    pass