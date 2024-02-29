import uuid
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Unicode, Sequence, Uuid, ForeignKey, UniqueConstraint, String, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column, composite
from core.db import Base
from core.db.mixins import AllMixin


class ProductCategory(Base, AllMixin):
    __tablename__ = "product_category"
    __table_args__ = (UniqueConstraint('external_id', 'company_id', name='_product_category_company_id_uc'),)
    lsn_seq = Sequence(f'product_category_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    title = Column(Unicode(255), nullable=False)
    parent_id = Column(Uuid, ForeignKey("product_category.id"), index=True, nullable=True)

class ProductStorageType(Base, AllMixin):
    __tablename__ = "product_storage_type"
    lsn_seq = Sequence(f'product_storage_type_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)

class ProductType(str, Enum):
    CONSUMABLE: str = 'consumable'
    STORABLE: str = 'storable'


class Product(Base, AllMixin):
    __tablename__ = "product"
    __table_args__ = (UniqueConstraint('external_id', 'company_id', name='_product_company_id_uc'),)
    lsn_seq = Sequence(f'product_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    description = Column(String, nullable=True)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    product_type = Column(Unicode(20), nullable=False, default=ProductType.STORABLE)
    uom_id = Column(Uuid, ForeignKey("uom.id"), index=True, nullable=False)
    uom = relationship("Uom", lazy='select', back_populates="products")
    product_category_id = Column(Uuid, ForeignKey("product_category.id"), index=True, nullable=False)
    product_storage_type_id = Column(Uuid, ForeignKey("product_storage_type.id"), index=True, nullable=False)
    barcodes: Mapped[list[str]] = mapped_column(type_=ARRAY(String), index=True, nullable=True)
