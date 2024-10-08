import uuid
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy import Uuid, Sequence, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column, Mapped

from .....db import Base
from .....db.mixins import AllMixin
from .....db.types import ids


class Role(Base, AllMixin):
    __tablename__ = "role"
    __table_args__ = (UniqueConstraint('title', 'company_id', name='_role_company_id_uc'),)
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    lsn_seq = Sequence(f'role_lsn_seq')
    title: Mapped[str] = mapped_column(index=True)
    role_ids: Mapped[Optional[ids]] = mapped_column(index=True, comment="Список дочерних ролей")
    permission_allow_list: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), server_default='{}', nullable=False, index=True)
    permission_deny_list: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), server_default='{}', nullable=False, index=False)
