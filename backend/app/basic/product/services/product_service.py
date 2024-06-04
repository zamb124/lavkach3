from sqlalchemy import select
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.basic.product.enums.exceptions_product_enums import ProductErrors
from app.basic.product.models.product_models import Product
from app.basic.product.schemas import ProductCreateScheme, ProductUpdateScheme, ProductFilter
from core.db.session import session
from core.exceptions.module import ModuleException
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class ProductService(BaseService[Product, ProductCreateScheme, ProductUpdateScheme, ProductFilter]):
    def __init__(self, request, db_session=None):
        super(ProductService, self).__init__(request, Product, ProductCreateScheme, ProductUpdateScheme, db_session)

    @permit('product_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(ProductService, self).update(id, obj)

    @permit('product_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(ProductService, self).list(_filter, size)

    @permit('product_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(ProductService, self).create(obj)

    @permit('product_delete')
    async def delete(self, id: Any) -> None:
        return await super(ProductService, self).delete(id)

    @permit('product_by_barcode')
    async def product_by_barcode(self, barcode: str):
        query = select(self.model)
        query = query.where(self.model.barcode_list.contains([barcode]))
        result = await self.session.execute(query)
        entity = result.scalars().first()
        if not entity:
            raise ModuleException(status_code=404, enum=ProductErrors.PRODUCT_NOT_FOUND)
        return entity
