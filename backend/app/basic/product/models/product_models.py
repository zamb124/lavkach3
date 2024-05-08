import uuid
from enum import Enum
from typing import Optional
from typing import TYPE_CHECKING

from sqlalchemy import Sequence, Uuid, ForeignKey, UniqueConstraint, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from core.db import Base
from core.db.mixins import AllMixin

if TYPE_CHECKING:
    from app.basic.uom.models import Uom


class ProductCategory(Base, AllMixin):
    __tablename__ = "product_category"
    __table_args__ = (UniqueConstraint('external_number', 'company_id', name='_product_category_company_id_uc'),)
    lsn_seq = Sequence(f'product_category_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    external_number: Mapped[Optional[str]]
    title: Mapped[str] = mapped_column(index=True)
    product_category_ids: Mapped[Optional[list[uuid.UUID]]] = mapped_column(ARRAY(Uuid), index=True)

class ProductType(str, Enum):
    CONSUMABLE: str = 'consumable'
    STORABLE: str = 'storable'


class Product(Base, AllMixin):
    __tablename__ = "product"
    __table_args__ = (UniqueConstraint('external_number', 'company_id', name='_product_company_id_uc'),)
    lsn_seq = Sequence(f'product_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[Optional[str]]
    external_number: Mapped[Optional[str]]
    product_type: Mapped[str] = mapped_column(default=ProductType.STORABLE)
    uom_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("uom.id"), index=True)
    uom_rel: Mapped['Uom'] = relationship(lazy='selectin')
    product_category_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("product_category.id"), index=True)
    barcode_list: Mapped[list[str]] = mapped_column(type_=ARRAY(String), index=True, nullable=True)
