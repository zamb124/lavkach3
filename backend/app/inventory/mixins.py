import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.inventory.location.enums import LocationClass


class LocationMixin:
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    location_class: Mapped[LocationClass] = mapped_column(index=True)
    partner_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)


class StockMixin(LocationMixin):
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, index=True
    )
    lot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("lot.id", ondelete="RESTRICT"), index=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(                   # локация
        ForeignKey("location.id", ondelete="RESTRICT"), index=True
    )
    package_id: Mapped[Optional[uuid.UUID]] = mapped_column(              # Упаковка, если есть
        ForeignKey("location.id", ondelete="RESTRICT"), index=True
    )
