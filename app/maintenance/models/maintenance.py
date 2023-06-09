from sqlalchemy import (
    Column, Unicode, BigInteger, Boolean, func, PickleType, JSON,
    UUID, ForeignKey, Sequence, Text, Integer, Numeric, DateTime
)

from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin, CompanyMixin
import uuid
from sqlalchemy.orm import RelationshipProperty, registry, relationship
from enum import Enum
from typing import List, Optional
from sqlalchemy.orm.decl_api import DeclarativeMeta

class Contractor(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "contractors"
    __allow_unmapped__ = True

    lsn_seq = Sequence(f'contractors_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    #servicesuppliers = relationship("ServiceSupplier", backref='contractor', lazy='selectin')
    #suppliers: List["ServiceSupplier"] = relationship("ServiceSupplier", backref="contractor", sa_relationship_kwargs={'lazy': 'selectin'})

class ServiceSupplier(Base, TimestampMixin):
    __tablename__ = "servicesuppliers"
    __allow_unmapped__ = True

    lsn_seq = Sequence(f'servicesuppliers_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    store_id = Column(UUID, ForeignKey("stores.id"), index=True, nullable=True)
    store = relationship("Store", backref='supplier_store', lazy='selectin')
    external_id = Column(Unicode(255), nullable=True, unique=True)
    contractor_id = Column(UUID,ForeignKey("contractors.id"), index=True, nullable=True)
    contractor = relationship("Contractor", backref='servicesuppliers',lazy='selectin')

class Manufacturer(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "manufacturers"
    lsn_seq = Sequence(f'manufacturers_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    #models = relationship("Model", backref='manufacturer', lazy='selectin')

class Model(Base, TimestampMixin):
    __tablename__ = "models"
    lsn_seq = Sequence(f'models_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    manufacturer_id = Column(UUID, ForeignKey("manufacturers.id"), index=True, nullable=True)
    manufacturer = relationship("Manufacturer", backref='models', lazy='selectin')

class Type(str, Enum):
    STORABLE: str = 'storable'
    CONSUMABLE: str = 'CONSUMABLE'


class SourceType(str, Enum):
    INTERNAL: str = 'internal'
    WMS: str = 'wms'
    OEBS: str = 'oebs'


class AssetType(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "assettypes"
    lsn_seq = Sequence(f'assettypes_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    type = Column(Unicode(20), nullable=False, default=Type.STORABLE)
    source = Column(Unicode(20), nullable=False, default=SourceType.INTERNAL)
    serial_required = Column(Boolean, default=True)


class AssetStatus(str, Enum):
    DRAFT: str = 'draft'
    ACTIVE: str = 'active'
    DAMAGED: str = 'damaged'
    SCRAPPED: str = 'scrapped'
class Asset(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "assets"
    lsn_seq = Sequence(f'assets_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    asset_type_id = Column(UUID, ForeignKey("assettypes.id"), index=True, nullable=True)
    asset_type = relationship("AssetType", backref='assets', lazy='selectin')
    manufacturer_id = Column(UUID, ForeignKey("manufacturers.id"), index=True, nullable=True)
    manufacturer = relationship("Manufacturer", backref='assets', lazy='selectin')
    store_id = Column(UUID, ForeignKey("stores.id"), index=True, nullable=True)
    store = relationship("Store", backref='assets', lazy='selectin')
    model_id = Column(UUID, ForeignKey("models.id"), index=True, nullable=True)
    model = relationship("Model", backref='assets', lazy='selectin')
    status = Column(Unicode(20), nullable=False, index=True, default=SourceType.INTERNAL)
    serial = Column(Unicode(255), nullable=True, index=True)
    at = Column(JSON, nullable=False, default={})
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    barcode = Column(UUID, nullable=False, index=True, unique=True)
    user = relationship("User", lazy='selectin')


class AssetLogAction(str, Enum):
    STORE_ID: str = 'store_id'
    COURIER_ID: str = 'at.courier_id'
    STATUS: str = 'status'
    INIT: str = 'init'
    ORDER_LINE: str = 'order_line'


class AssetLog(Base, TimestampMixin):
    __tablename__ = "assets_log"
    serial = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, default=func.now(), nullable=False)
    asset_id = Column(UUID, ForeignKey("assets.id"), index=True, nullable=False)
    action = Column(Unicode(30), nullable=False)
    from_ = Column(Unicode(255), nullable=True)
    to = Column(Unicode(255), nullable=True)


class OrderStatus(str, Enum):
    DRAFT = 'draft'
    FREE = 'free'
    TAKEN = 'taken'
    IN_PROGRESS = 'in_progress'
    FINISHING = 'finishing'
    DONE = 'done'

class Order(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "orders"
    __allow_unmapped__ = True

    lsn_seq = Sequence(f'orders_lsn_seq')
    number_seq = Sequence(f'orders_number_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    number = Column(BigInteger, number_seq, default=number_seq.next_value(), index=True)
    description = Column(Text, nullable=True)
    supplier_id = Column(UUID, index=True, nullable=True)
    status = Column(Unicode(30), nullable=False, index=True, default=OrderStatus.DRAFT)
    asset_id = Column(UUID, ForeignKey("assets.id"), index=True, nullable=False)
    asset = relationship("Asset", backref='asset_orders', lazy='selectin')
    store_id = Column(UUID, ForeignKey("stores.id"), index=True, nullable=True)
    store = relationship("Store", backref='order_store', lazy='selectin')
    user_created_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    user_created = relationship("User", lazy='selectin', foreign_keys=[user_created_id])
    supplier_user_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    supplier_user = relationship("User", lazy='selectin', foreign_keys=[supplier_user_id])
    order_lines = relationship("OrderLine", lazy='selectin')

class OrderLine(Base, TimestampMixin):
    __tablename__ = "orders_lines"
    __allow_unmapped__ = True

    lsn_seq = Sequence(f'orders_lines_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    description = Column(Text, nullable=True)
    order_id = Column(UUID, ForeignKey("orders.id"), index=True, nullable=True)
    order = relationship("Order",viewonly=True, lazy='joined')
    quantity = Column(Integer, nullable=False, default=1)
    cost = Column(Numeric(12, 2), default=0.0)