import uuid
from typing import Optional

from sqlalchemy import Sequence, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base
from core.db.mixins import AllMixin
from core.db.types import ids


class StorageType(Base, AllMixin):
    __tablename__ = "storage_type"
    lsn_seq = Sequence(f'storage_type_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    title: Mapped[str]
    priority: Mapped[int]  # Приоритет данной стратегии хранения
    location_ids: Mapped[ids]


class ProductStorageType(Base, AllMixin):
    """
        Расширяет Product добавляя к нему нужные для склада(если нужно) свойства
        storage_uom_id - если ЕИ отлична от базовой
        storage_image_url - Если картинка товара для склада отличается от базовой
        allowed_package_ids - в какие типы упаковок можно класть товар
        exclude_package_ids - в какие нельзя
        is_homogeneity - товар гомогенен
    """
    __tablename__ = "product_storage_type"
    lsn_seq = Sequence(f'product_storage_type_lsn_seq')
    __table_args__ = (UniqueConstraint('product_id', 'company_id', name='stor_type_product_company_id_uc'),)
    product_id: Mapped[uuid.UUID] = mapped_column(index=True)
    storage_uom_id: Mapped[Optional[uuid.UUID]]         # Единица измерения склада
    storage_image_url: Mapped[Optional[str]]            # Картинка для склада
    allowed_package_ids: Mapped[Optional[ids]] = mapped_column(index=True)  # Разрешенные типы упаковок
    exclude_package_ids: Mapped[Optional[ids]] = mapped_column(index=True)  # Исключение типы упаковок
    is_homogeneity: Mapped[bool] = mapped_column(default=False)  # Товар может хранится только в гомогенных ячейках
    is_mix_products: Mapped[Optional[bool]] = mapped_column(default=False)  # товар может хранится в микс ячейках
    storage_type_ids: Mapped[Optional[ids]] = mapped_column(default=False)  # Стратегии хранения
