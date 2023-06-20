from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey, Sequence, Enum, Text, Integer, DECIMAL, Numeric
from sqlalchemy import Column, Unicode, BigInteger, Boolean, UUID, ForeignKey, Sequence
from sqlalchemy_utils import CurrencyType, Currency, CountryType, LocaleType
from core.db import Base
from core.db.mixins import TimestampMixin, LsnMixin, CompanyMixin, AllMixin
import uuid
from enum import Enum
from sqlalchemy.orm import relationship
class PurchaseOrderStatus(str, Enum):
    DRAFT: str = 'draft'
    RFQ: str = 'rfq'
    CONFIRMED: str = 'confirmed'
    SENT: str = 'sent'
    STOWAGING: str = 'stowaging'
    DONE: str = 'done'
    CANCELLED: str = 'cancelled'

class PurchaseOrder(Base, AllMixin):
    __tablename__ = "purchase_order"
    __allow_unmapped__ = True
    lsn_seq = Sequence(f'purchase_order_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)

    ref = Column(Unicode(200), nullable=True)
    partner_id = Column(UUID, ForeignKey("partner.id"), index=True, nullable=True)
    partner = relationship("Partner", lazy='selectin')
    store_id = Column(UUID, ForeignKey("store.id"), index=True, nullable=True)
    store = relationship("Store", lazy='selectin')
    #contract_id = Column(UUID, ForeignKey("contract.id"), index=True, nullable=True)
    #contract = relationship("Contract", lazy='selectin')
    status = Column(Unicode(30), nullable=False, index=True, default=PurchaseOrderStatus.DRAFT)
    created_user_id = Column(UUID, ForeignKey("user.id"), index=True, nullable=False)
    order_lines = relationship("PurchaseOrderLine", lazy='selectin')


class PurchaseOrderLine(Base, AllMixin):
    __tablename__ = "orders_line"
    __allow_unmapped__ = True

    lsn_seq = Sequence(f'orders_line_lsn_seq')
    lsn = Column(BigInteger, lsn_seq, onupdate=lsn_seq.next_value(), index=True)
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(Unicode(255), nullable=False)

    description = Column(Text, nullable=True)
    order_id = Column(UUID, ForeignKey("orders.id"), index=True, nullable=True)
    order = relationship("PurchaseOrder", viewonly=True, lazy='joined')
    uom_id = Column(UUID, ForeignKey("Uom.id"), index=True, nullable=True)
    uom = relationship("Uom", lazy='joined')
    quantity = Column(Integer, nullable=False, default=1)
    cost = Column(Numeric(12, 2), default=0.0)
    currency = Column(CurrencyType, nullable=False)