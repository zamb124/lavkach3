from typing import Optional, List
from uuid import UUID

from fastapi_filter.contrib.sqlalchemy import Filter

from app.inventory.product_storage.models.product_storage_models import StorageType
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel, BasicField as Field
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class StorageTypeBaseScheme(BasicModel):
    """"""
    product_id: UUID = Field(title='Product', form=True, model='product')
    storage_uom_id: Optional[UUID] = Field(default=None)  # Единица измерения склада
    title: str = Field(title='Title', form=True)
    priority: int = Field(title='Priority', form=True)  # Приоритет данной стратегии хранения
    location_ids: Optional[List[UUID]] = Field(default=[], title='Locations', model='location')  # Список идентификаторов ячеек хранения

    class Config:
        orm_model = StorageType


class StorageTypeUpdateScheme(StorageTypeBaseScheme):
    ...


class StorageTypeCreateScheme(StorageTypeBaseScheme):
    ...


class StorageTypeScheme(StorageTypeCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID = Field(title='ID', form=False)


class StorageTypeFilter(BaseFilter):
    product_id__in: Optional[List[UUID]] = Field(default=False, title='Product', form=True, model='product')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = StorageType
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["product_id", ]


class StorageTypeListSchema(GenericListSchema):
    data: Optional[List[StorageTypeScheme]]
