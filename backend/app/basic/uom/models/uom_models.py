import uuid
from typing import Optional
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Sequence, Integer
from sqlalchemy import Numeric, Uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.basic.uom.enums.uom_enum import UomType
from core.db import Base
from core.db.mixins import AllMixin

if TYPE_CHECKING:
    from app.basic.uom.models.uom_category_models import UomCategory



class Uom(Base, AllMixin):
    """
    Ratio (коэффициент) представляет собой множитель, который используется для конвертации данной единицы измерения в
    эталонную единицу измерения в рамках одной категории. Например, если у вас есть единица измерения "килограмм" с
    коэффициентом 1 и единица измерения "грамм" с коэффициентом 1000, это означает, что 1 килограмм равен 1000 граммам.

    Precision (точность) определяет количество знаков после запятой, которые будут использоваться при округлении
    значений. Это важно для обеспечения точности вычислений при конвертации между различными единицами измерения.
    Например, если точность установлена на 2, то значения будут округляться до двух знаков после запятой.
    """
    __tablename__ = "uom"

    lsn_seq = Sequence(f'uom_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    uom_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("uom_category.id"))
    uom_category_rel: Mapped['UomCategory'] = relationship(back_populates='uom_list_rel', lazy='selectin')
    type: Mapped[str] = mapped_column(index=True, default=UomType.STANDART)
    ratio: Mapped[float] = mapped_column(Numeric(12, 2), default=1)
    precision: Mapped[int] = mapped_column(Integer, default=2)
