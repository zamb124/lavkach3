from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey, Sequence

from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin, CompanyMixin
import uuid
#from sqlalchemy.orm import relationship
from enum import Enum


class Contractor(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "contractors"
    lsn_seq = Sequence(f'contractors_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    external_id = Column(Unicode(255), nullable=True, unique=True)

class ServiceSupplier(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "servicesuppliers"
    lsn_seq = Sequence(f'servicesuppliers_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    external_id = Column(Unicode(255), nullable=True, unique=True)
    #contractor_id = Column(UUID,ForeignKey("contractors.id"), index=True, nullable=True)
    #contractor = relationship("Contractor", backref="suppliers")

class Manufacturer(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "manufacturers"
    lsn_seq = Sequence(f'manufacturers_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)

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


class Model(Base, TimestampMixin, CompanyMixin):
    __tablename__ = "models"
    lsn_seq = Sequence(f'models_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)
    manufacturer_id = Column(UUID, ForeignKey("manufacturers.id"), index=True, nullable=True)
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
    manufacturer_id = Column(UUID, ForeignKey("manufacturers.id"), index=True, nullable=True)
    store_id = Column(UUID, ForeignKey("stores.id"), index=True, nullable=True)
    model_id = Column(UUID, ForeignKey("models.id"), index=True, nullable=True)
    status = Column(Unicode(20), nullable=False, index=True, default=SourceType.INTERNAL)
    serial = Column(Unicode(255), nullable=True, index=True)
    at = Column(Unicode(255), nullable=True)
    owner = Column(UUID, ForeignKey("users.id"), nullable=True)