import datetime
import uuid

from sqlalchemy import Column, DateTime, func, Uuid, BigInteger, ForeignKey, Sequence, text, types
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy_utils.types import JSONType
from typing import Annotated, Optional

from sqlalchemy import DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression


# UTC now function on database server
class UTCNow(
    expression.FunctionElement  # type: ignore[name-defined]
):  # pylint: disable=too-many-ancestors
    type = DateTime()


@compiles(UTCNow, "postgresql")  # type: ignore[misc]
def pg_utcnow(  # type: ignore[no-untyped-def]
        element, compiler, **kw  # pylint: disable=unused-argument
) -> str:
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

guid_primary_key = mapped_column(
        types.Uuid,
        primary_key=True,
        init=False,
        server_default=text("gen_random_uuid()")
    )
guid = mapped_column(
        types.Uuid,
        init=False,
        index=True,
        server_default=text("gen_random_uuid()")
    )
class VarsMixin:
    vars: Mapped[dict] = mapped_column(JSONType, nullable=False, default={})

class TimestampMixin:
    created_at: Mapped[datetime.datetime] = Column(
        DateTime(),
        nullable=False,
        server_default=UTCNow()
    )

    updated_at: Mapped[datetime.datetime] = Column(
        DateTime(),
        nullable=True,
        server_default=UTCNow(),
        server_onupdate=UTCNow(),
    )


class CompanyMixin:
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("company.id"), index=True, nullable=False)

class CreatedEdited:
    created_by: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)
    edited_by: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)


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
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)