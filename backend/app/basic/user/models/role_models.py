import uuid

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table, UniqueConstraint
from sqlalchemy import Unicode, Boolean, Uuid, Sequence, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin


class Role(Base, AllMixin):
    __tablename__ = "role"
    __table_args__ = (UniqueConstraint('title', 'company_id', name='_role_company_id_uc'),)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    lsn_seq = Sequence(f'role_lsn_seq')
    title = Column(Unicode(255), nullable=False)
    parents = Column(ARRAY(Uuid), index=True, nullable=True)
    permissions_allow = Column(ARRAY(String), index=True, nullable=True)
    permissions_deny = Column(ARRAY(String), index=False, nullable=True)


