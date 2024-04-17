from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.basic.product.models.product_models import ProductStorageType
from app.basic.product.schemas import ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, ProductStorageTypeFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class ProductStorageTypeService(BaseService[ProductStorageType, ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, ProductStorageTypeFilter]):
    def __init__(self, request, db_session=None):
        super(ProductStorageTypeService, self).__init__(request, ProductStorageType, ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, db_session)

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
