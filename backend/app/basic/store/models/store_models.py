import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import Sequence, Uuid
from sqlalchemy.orm import mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin


class SourceType(str, Enum):
    """
        Источник данных
    """
    INTERNAL: str = 'internal'
    WMS: str = 'wms'


class Type(str, Enum):
    """
        Тип скдада
            - simple: Хранение ведется на уровне товара
            - ZOME: Хранение ведется на уровне зон/помещений
            - SHELF: Хранение ведется на уровне полок
    """
    SIMPLE: str = 'simple'
    ZONE: str = 'zone'
    SHELF: str = 'shelf'


class Store(Base, AllMixin):
    __tablename__ = "store"
    lsn_seq = Sequence(f'store_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(index=True)
    external_number: Mapped[Optional[str]] = mapped_column(unique=True)
    address: Mapped[str]
    source: Mapped[str] = mapped_column(default=SourceType.INTERNAL)
    type: Mapped[str] = mapped_column(default=Type.SIMPLE)
