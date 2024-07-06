import datetime
import uuid
from typing import Optional

from sqlalchemy import Sequence, Uuid, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped

# from app.inventory.location.models import Location, LocationClass
from app.inventory.order.enums.order_enum import OrderStatus
from app.inventory.quant.models import Lot
from core.db import Base
from core.db.mixins import AllMixin, CreatedEdited
from core.db.types import ids


class Document(Base, AllMixin, CreatedEdited):
    """
    Документ, который является основанием для изменения запаса
    """
    __tablename__ = "document"
    __table_args__ = (
        UniqueConstraint('external_number', 'company_id', name='_document_companyid_external_number_uc'),
    )
    lsn_seq = Sequence(f'document_lsn_seq')
    number: Mapped[str] = mapped_column(index=True)    # Человекочитаемый номер присвается по формуле - {ГОД(2)}-{МЕСЯЦ}-{ДЕНЬ}-{LSN}
    external_number: Mapped[Optional[str]]
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)
    lot_id: Mapped[Optional['Lot']] = mapped_column(ForeignKey("lot.id", ondelete="SET NULL"))
    origin_type: Mapped[Optional[str]] = mapped_column(index=True)
    origin_number: Mapped[Optional[str]] = mapped_column(index=True)
    planned_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    actual_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    expiration_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    user_ids: Mapped[Optional[ids]] = mapped_column(index=True)
    description: Mapped[Optional[str]]
    status: Mapped['OrderStatus'] = mapped_column(default=OrderStatus.DRAFT)
    move_list_rel: Mapped[Optional[list["Move"]]] = relationship(back_populates="order_rel", lazy="selectin")

    def __init__(self, **kwargs):
        """
            Разрешает экстра поля, но удаляет, если их нет в табличке
        """
        allowed_args = self.__mapper__.class_manager  # returns a dict
        kwargs = {k: v for k, v in kwargs.items() if k in allowed_args}
        super().__init__(**kwargs)


