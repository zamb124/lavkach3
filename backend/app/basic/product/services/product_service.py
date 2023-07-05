from typing import Any, Optional

from starlette.requests import Request

from app.basic.store.models.store_models import Store
from app.basic.store.schemas.store_schemas import StoreCreateScheme, StoreUpdateScheme, StoreFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class StoreService(BaseService[Store, StoreCreateScheme, StoreUpdateScheme, StoreFilter]):
    def __init__(self, request: Request, db_session: session=session):
        super(StoreService, self).__init__(request, Store, db_session)

    @permit('store_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(StoreService, self).update(id, obj)

    @permit('store_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(StoreService, self).list(_filter, size)

    @permit('store_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(StoreService, self).create(obj)

    @permit('store_delete')
    async def delete(self, id: Any) -> None:
        return await super(StoreService).delete(id)
