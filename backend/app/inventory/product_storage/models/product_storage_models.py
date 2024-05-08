import uuid
from typing import Optional

from sqlalchemy import Sequence, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base
from core.db.mixins import AllMixin


class ProductStorageType(Base, AllMixin):
    """
        Определяет некую стратегию размещение товара на складе
        Те если у товара есть такой обьект, внутри него определяется правило куда и в каких зонах он будет размещатся
        Если таких обьектав у товара несколько то это будет приоритизироваться
    """
    __tablename__ = "product_storage_type"
    lsn_seq = Sequence(f'product_storage_type_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    external_number: Mapped[Optional[str]]
    title: Mapped[str] = mapped_column(index=True)
