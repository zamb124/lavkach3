from typing import Any, Optional

from app.inventory.product_storage.models.product_storage_models import ProductStorageType
from app.inventory.product_storage.schemas import ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, \
    ProductStorageTypeFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType
from starlette.requests import Request

class ProductStorageTypeService(BaseService[ProductStorageType, ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, ProductStorageTypeFilter]):
    def __init__(self, request:Request):
        super(ProductStorageTypeService, self).__init__(request, ProductStorageType, ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme,)

    @permit('product_storage_type_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(ProductStorageTypeService, self).update(id, obj)

    @permit('product_storage_type_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(ProductStorageTypeService, self).list(_filter, size)

    @permit('product_storage_type_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(ProductStorageTypeService, self).create(obj)

    @permit('product_storage_type_delete')
    async def delete(self, id: Any) -> None:
        return await super(ProductStorageTypeService, self).delete(id)
