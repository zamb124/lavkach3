import uuid
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table, UniqueConstraint
from sqlalchemy import Unicode, Boolean, Uuid, Sequence, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin
from core.db.types import ids


class Role(Base, AllMixin):
    __tablename__ = "role"
    __table_args__ = (UniqueConstraint('title', 'company_id', name='_role_company_id_uc'),)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    lsn_seq = Sequence(f'role_lsn_seq')
    title: Mapped[str] = mapped_column(index=True)
    role_ids: Mapped[Optional[ids]] = mapped_column(ARRAY(Uuid), index=True)
    permission_allow_list: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), index=True, default=[])
    permission_deny_list: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), index=False, default=[])


