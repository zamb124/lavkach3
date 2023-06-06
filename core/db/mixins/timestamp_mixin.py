from sqlalchemy import Column, DateTime, func, UUID
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
    def company_id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            index=True,
            default=uuid.uuid4
        )
