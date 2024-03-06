from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.basic.product.models.product_models import ProductCategory
from app.basic.product.schemas import ProductCategoryCreateScheme, ProductCategoryUpdateScheme, ProductCategoryFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class ProductCategoryService(BaseService[ProductCategory, ProductCategoryCreateScheme, ProductCategoryUpdateScheme, ProductCategoryFilter]):
    def __init__(self, request, db_session):
        super(ProductCategoryService, self).__init__(request, ProductCategory, db_session)

    @permit('product_category_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(ProductCategoryService, self).update(id, obj)

    @permit('product_category_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(ProductCategoryService, self).list(_filter, size)

    @permit('product_category_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(ProductCategoryService, self).create(obj)

    @permit('product_category_delete')
    async def delete(self, id: Any) -> None:
        return await super(ProductCategoryService, self).delete(id)
