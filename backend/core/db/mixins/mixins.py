import datetime

from sqlalchemy import Column, DateTime, func, Uuid, BigInteger, ForeignKey, Sequence, text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy_utils.types import JSONType
from typing import Annotated, Optional

created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"),
    onupdate=datetime.datetime.utcnow,
)]


class VarsMixin:
    @declared_attr
    def vars(cls):  # company_id = Column(UUID, ForeignKey("companies.id"))
        return Column(
            JSONType,
            nullable=True
        )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CompanyMixin:
    company_id: Mapped[Uuid] = mapped_column(ForeignKey("company.id"), index=True, nullable=False)


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


class AllMixin(LsnMixin, CompanyMixin, TimestampMixin, VarsMixin):
    pass
