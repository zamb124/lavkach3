from typing import Any, Optional, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from starlette.requests import Request

from app.inventory.product_storage.models.product_storage_models import ProductStorageType
from app.inventory.product_storage.schemas import ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, \
    ProductStorageTypeFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class ProductStorageTypeService(BaseService[
                                    ProductStorageType, ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, ProductStorageTypeFilter]):
    def __init__(self, request: Request):
        super(ProductStorageTypeService, self).__init__(request, ProductStorageType, ProductStorageTypeCreateScheme,
                                                        ProductStorageTypeUpdateScheme, )

    @permit('product_storage_type_update')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(ProductStorageTypeService, self).update(id, obj)

    @permit('product_storage_type_list')
    async def list(self, _filter: FilterSchemaType, size: int = 100):
        return await super(ProductStorageTypeService, self).list(_filter, size)

    @permit('product_storage_type_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(ProductStorageTypeService, self).create(obj)

    @permit('product_storage_type_delete')
    async def delete(self, id: Any) -> None:
        return await super(ProductStorageTypeService, self).delete(id)

    async def get_storage_types_by_products(self, product_ids) -> List[ProductStorageType]:
        result = await self.session.execute(
            select(ProductStorageType)
            .options(joinedload(ProductStorageType.storage_type_rel))
            .where(ProductStorageType.product_id.in_(product_ids))
        )
        product_storage_types = result.scalars().all()

        return product_storage_types
