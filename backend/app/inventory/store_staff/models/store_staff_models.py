import uuid
from typing import Optional

from sqlalchemy import Sequence, Uuid, ForeignKey, text
from sqlalchemy.orm import mapped_column, Mapped

from app.inventory.store_staff.enums import StaffPosition
from core.db import Base
from core.db.mixins import AllMixin
from core.db.types import ids


class StoreStaff(Base, AllMixin):
    """
        Сотрудники склада (user inventory profile)
        - user_id Ссылка на сотрудника (пользователя)
        - store_id Магазин(store), к которому привязан
        - store_ids Список магазинов, к которым есть доступ и может привязаться
        - staff_position Тип сотрудника (класс)
        - staff_number Идентификатор сотрудника (табельный номер)
        - external_number Внешний идентификатор

    """
    __tablename__ = "store_staff"
    lsn_seq = Sequence(f'store_staff_lsn_seq')
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True)
    staff_position: Mapped['StaffPosition'] = mapped_column(default=StaffPosition.STOREKEEPER, index=True)
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    store_ids: Mapped[ids] = mapped_column(index=True)
    staff_number: Mapped[Optional[str]] = mapped_column(index=True, nullable=True)
    external_number: Mapped[Optional[str]] = mapped_column(index=True, nullable=True)

