from typing import Optional, List
from uuid import UUID

from fastapi_filter.contrib.sqlalchemy import Filter

from app.inventory.product_storage.models.product_storage_models import ProductStorageType
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel, BasicField as Field
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class ProductStorageTypeBaseScheme(BasicModel):
    product_id: UUID = Field(title='Product', form=True, model='product')
    storage_uom_id: Optional[UUID] = Field(default=None)  # Единица измерения склада
    storage_image_url: Optional[str] = Field(default=None)  # Картинка для склада
    allowed_storage_uom_ids: Optional[List[UUID]] = Field(default=[])  # Разрешенные единицы измерения склада
    allowed_package_type_ids: Optional[List[UUID]] = Field(default=[])  # Разрешенные типы упаковок
    is_homogeneity: bool = Field(default=False)  # Товар может хранится только в гомогенных ячейках
    storage_type_id: UUID = Field(title='Storage Type ', form=True, model='storage_type')  # Стратегии хранения

    class Config:
        orm_model = ProductStorageType


class ProductStorageTypeUpdateScheme(ProductStorageTypeBaseScheme):
    ...


class ProductStorageTypeCreateScheme(ProductStorageTypeBaseScheme):
    ...


class ProductStorageTypeScheme(ProductStorageTypeCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID = Field(title='ID', form=False)


class ProductStorageTypeFilter(BaseFilter):
    product_id__in: Optional[List[UUID]] = Field(default=False, title='Product', form=True, model='product')

    class Constants(Filter.Constants):
        model = ProductStorageType
        search_model_fields = []


class ProductStorageTypeListSchema(GenericListSchema):
    data: Optional[List[ProductStorageTypeScheme]]
