import uuid
from enum import Enum

from sqlalchemy import (
    Column, Unicode, BigInteger, Boolean, Uuid, ForeignKey, Sequence, Text, Integer, Numeric
)
from sqlalchemy.orm import relationship

from core.db import Base
from core.db.mixins import TimestampMixin, CompanyMixin


class Manufacturer(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "manufacturer"
    lsn_seq = Sequence(f'manufacturer_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid(as_uuid=False), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    # models = relationship("Model", backref='manufacturer', lazy='selectin')


class Model(Base, TimestampMixin):
    __tablename__ = "model"
    lsn_seq = Sequence(f'model_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid(as_uuid=False), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    manufacturer_id = Column(Uuid, ForeignKey("manufacturer.id"), index=True, nullable=True)
    manufacturer = relationship("Manufacturer", backref='models', lazy='selectin')


class Type(str, Enum):
    STORABLE: str = 'storable'
    CONSUMABLE: str = 'CONSUMABLE'


class SourceType(str, Enum):
    INTERNAL: str = 'internal'
    WMS: str = 'wms'
    OEBS: str = 'oebs'


class AssetType(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "asset_type"
    lsn_seq = Sequence(f'asset_type_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid(as_uuid=False), primary_key=True, index=True, default=uuid.uuid4)
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
    __tablename__ = "asset"
    lsn_seq = Sequence(f'asset_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid(as_uuid=False), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    asset_type_id = Column(Uuid, ForeignKey("asset_type.id"), index=True, nullable=True)
    asset_type = relationship("AssetType", lazy='selectin')
    manufacturer_id = Column(Uuid, ForeignKey("manufacturer.id"), index=True, nullable=True)
    manufacturer = relationship("Manufacturer", lazy='selectin')
    store_id = Column(Uuid, ForeignKey("store.id"), index=True, nullable=True)
    store = relationship("Store", lazy='selectin')
    model_id = Column(Uuid, ForeignKey("model.id"), index=True, nullable=True)
    model = relationship("Model", lazy='selectin')
    status = Column(Unicode(20), nullable=False, index=True, default=AssetStatus.DRAFT)
    at_user_id = Column(Uuid, ForeignKey("user.id"), nullable=True)
    at_user = relationship("User", lazy='selectin', foreign_keys=[at_user_id])
    user_created_id = Column(Uuid, ForeignKey("user.id"), nullable=True)
    barcode = Column(Unicode(1000), nullable=False, index=True, unique=True)
    user_created = relationship("User", lazy='selectin', foreign_keys=[user_created_id])
    orders = relationship("Order", lazy='selectin')
    asset_logs = relationship("AssetLog", lazy='selectin')


class AssetLogAction(str, Enum):
    STORE_ID: str = 'store_id'
    COURIER_ID: str = 'at_user_id'
    STATUS: str = 'status'
    INIT: str = 'init'
    ORDER_LINE: str = 'order_line'


class AssetLog(Base, TimestampMixin):
    __tablename__ = "asset_log"
    lsn_seq = Sequence(f'asset_log_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid(as_uuid=False), primary_key=True, index=True, default=uuid.uuid4)
    asset_id = Column(Uuid, ForeignKey("asset.id"), index=True, nullable=False)
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
    __tablename__ = "order"
    __allow_unmapped__ = True

    lsn_seq = Sequence(f'order_lsn_seq')
    number_seq = Sequence(f'order_number_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid(as_uuid=False), primary_key=True, index=True, default=uuid.uuid4)
    number = Column(BigInteger, number_seq, default=number_seq.next_value(), index=True)
    description = Column(Text, nullable=True)
    partner_id = Column(Uuid, ForeignKey("partner.id"), index=True, nullable=True)
    status = Column(Unicode(30), nullable=False, index=True, default=OrderStatus.DRAFT)
    asset_id = Column(Uuid, ForeignKey("asset.id"), index=True, nullable=False)

    store_id = Column(Uuid, ForeignKey("store.id"), index=True, nullable=True)
    store = relationship("Store", lazy='selectin')
    user_created_id = Column(Uuid, ForeignKey("user.id"), nullable=True)
    user_created = relationship("User", lazy='selectin', foreign_keys=[user_created_id])
    partner_user_id = Column(Uuid, ForeignKey("user.id"), nullable=True)
    partner_user = relationship("User", lazy='selectin', foreign_keys=[partner_user_id])
    order_lines = relationship("OrderLine", lazy='selectin')


class OrderLine(Base, TimestampMixin):
    __tablename__ = "order_line"
    __allow_unmapped__ = True

    lsn_seq = Sequence(f'order_line_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(Uuid(as_uuid=False), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    description = Column(Text, nullable=True)
    order_id = Column(Uuid, ForeignKey("order.id"), index=True, nullable=True)
    order = relationship("Order", viewonly=True, lazy='joined')
    quantity = Column(Integer, nullable=False, default=1)
    cost = Column(Numeric(12, 2), default=0.0)
