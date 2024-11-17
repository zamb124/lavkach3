import uuid
from typing import Optional, List, Dict

from sphinx.addnodes import index
from sqlalchemy import Sequence, Uuid, UniqueConstraint, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.db.mixins import AllMixin
from core.db.types import ids


class StorageType(Base, AllMixin):
    """
        По сути является стратегией поиска локаций для хранения товаров.
    """
    __tablename__ = "storage_type"
    lsn_seq = Sequence(f'storage_type_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    partner_id: Mapped[Optional[uuid.UUID]]                             # Партнер
    store_id: Mapped[Optional[uuid.UUID]]                               # Склад
    title: Mapped[str]                                                  # Название стратегии
    allowed_location_type_ids: Mapped[ids]                              # Разрешенные типы локаций
    allowed_zones: Mapped[Optional[list[dict[str, uuid.UUID, int]]]] = mapped_column(JSON)   # Разрешенные зоны с приоритетами



class ProductStorageType(Base, AllMixin):
    """
    Расширяет Product, добавляя к нему нужные для склада (если нужно) свойства.

    Атрибуты:
    ----------
    storage_uom_id : uuid
        Идентификатор единицы измерения склада, если ЕИ отличается от базовой.
    storage_image_url : str
        URL изображения товара для склада, если картинка отличается от базовой.
    allowed_package_ids : List[uuid]
        Список идентификаторов типов упаковок, в которые можно класть товар.
    is_homogeneity : bool
        Флаг, указывающий, может ли товар храниться только в гомогенных ячейках.
    storage_type_ids : List[uuid]
        Идентификаторы стратегий хранения товара.
    """
    __tablename__ = "product_storage_type"
    lsn_seq = Sequence(f'product_storage_type_lsn_seq')
    __table_args__ = (UniqueConstraint('product_id', 'company_id', name='stor_type_product_company_id_uc'),)
    product_id: Mapped[uuid.UUID] = mapped_column(index=True)
    storage_uom_id: Mapped[Optional[uuid.UUID]]         # Единица измерения склада
    allowed_storage_uom_ids: Mapped[Optional[ids]]  # Разрешенные единицы измерения склада
    storage_image_url: Mapped[Optional[str]]            # Картинка для склада
    allowed_package_ids: Mapped[Optional[ids]]
    is_homogeneity: Mapped[bool] = mapped_column(default=False, index=True)  # Товар может хранится только в гомогенных ячейках
    storage_type_id: Mapped[Optional[uuid.UUID]]  = mapped_column(ForeignKey("storage_type.id"))      # Стратегия хранения товара
    storage_type_rel: Mapped[Optional[StorageType]] = relationship(lazy="noload")
