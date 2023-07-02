import uuid

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table, UniqueConstraint
from sqlalchemy import Unicode, Boolean, Uuid, Sequence, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from core.db import Base
from core.db.mixins import AllMixin

roles_assotiation = Table(
    "roles_assotiation",
    Base.metadata,
    Column('parent_role_id', Uuid, ForeignKey("role.id"), primary_key=True),
    Column('child_role_id', Uuid, ForeignKey("role.id"), primary_key=True),
    Column('active', Boolean, default=True)
)


class Role(Base, AllMixin):
    __tablename__ = "role"
    __table_args__ = (UniqueConstraint('title', 'company_id', name='_role_company_id_uc'),)
    id = Column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    lsn_seq = Sequence(f'role_lsn_seq')
    title = Column(Unicode(255), nullable=False)
    parents = relationship(
        "Role",
        secondary=roles_assotiation,
        primaryjoin=roles_assotiation.c.parent_role_id == id,
        secondaryjoin=roles_assotiation.c.child_role_id == id,
        backref="childrens")
    permissions_allow = Column(ARRAY(String), index=False, nullable=True)
    permissions_deny = Column(ARRAY(String), index=False, nullable=True)


