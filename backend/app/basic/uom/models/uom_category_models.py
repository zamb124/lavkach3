import uuid

from sqlalchemy import Sequence
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin


class UomCategory(Base, AllMixin):
    __tablename__ = "uom_category"
    lsn_seq = Sequence(f'uom_category_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    uoms: Mapped['Uom'] = relationship(back_populates='category', lazy='selectin')
