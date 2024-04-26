import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, Sequence
from sqlalchemy import Numeric, Uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING

from app.basic.uom.enums.uom_enum import UomType
from core.db import Base
from core.db.mixins import AllMixin
if TYPE_CHECKING:
    from app.basic.product.models import Product
    from app.basic.uom.models.uom_category_models import UomCategory



class Uom(Base, AllMixin):
    __tablename__ = "uom"

    lsn_seq = Sequence(f'uom_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    uom_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("uom_category.id"))
    uom_category_rel: Mapped['UomCategory'] = relationship(back_populates='uom_list_rel', lazy='selectin')
    type: Mapped[str] = mapped_column(index=True, default=UomType.STANDART)
    ratio: Mapped[float] = mapped_column(Numeric(12, 2), default=1)
    precision: Mapped[float] = mapped_column(Numeric(12, 2), default=0.01)
