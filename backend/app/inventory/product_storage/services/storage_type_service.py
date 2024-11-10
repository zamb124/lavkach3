from typing import Any, Optional

from app.inventory.product_storage.models.product_storage_models import StorageType
from app.inventory.product_storage.schemas import StorageTypeCreateScheme, StorageTypeUpdateScheme, \
    StorageTypeFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType
from starlette.requests import Request


class StorageTypeService(BaseService[StorageType, StorageTypeCreateScheme, StorageTypeUpdateScheme, StorageTypeFilter]):
    def __init__(self, request: Request):
        super(StorageTypeService, self).__init__(request, StorageType, StorageTypeCreateScheme,
                                                 StorageTypeUpdateScheme, )

    @permit('storage_type_update')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(StorageTypeService, self).update(id, obj)

    @permit('storage_type_list')
    async def list(self, _filter: FilterSchemaType, size: int=100):
        return await super(StorageTypeService, self).list(_filter, size)

    @permit('storage_type_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(StorageTypeService, self).create(obj)

    @permit('storage_type_delete')
    async def delete(self, id: Any) -> None:
        return await super(StorageTypeService, self).delete(id)
