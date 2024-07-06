from typing import Any, Optional

from starlette.requests import Request

from app.basic.store.models.store_models import Store
from app.basic.store.schemas.store_schemas import StoreCreateScheme, StoreUpdateScheme, StoreFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class StoreService(BaseService[Store, StoreCreateScheme, StoreUpdateScheme, StoreFilter]):
    def __init__(self, request:Request):
        super(StoreService, self).__init__(request, Store,StoreCreateScheme, StoreUpdateScheme)

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
        return await super(StoreService, self).delete(id)

    @permit('assign_store')
    async def assign_store(self, store_id: Any) -> None:
        store_entity = await self.get(store_id)
        user_entity = await self.env['user'].service.get(self.user.user_id)
        user_entity.store_id = store_entity.id
        self.session.add(user_entity)
        await self.session.commit()
        return {
            'status': 'OK',
            'detail': 'User has been assigned the store'
        }

