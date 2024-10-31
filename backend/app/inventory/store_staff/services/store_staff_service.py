from typing import Any
from uuid import UUID

from sqlalchemy import Row
from starlette.requests import Request

from app.inventory.store_staff.models.store_staff_models import StoreStaff
from app.inventory.store_staff.schemas.store_staff_schemas import StoreStaffCreateScheme, StoreStaffUpdateScheme, \
    StoreStaffFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class StoreStaffService(BaseService[StoreStaff, StoreStaffCreateScheme, StoreStaffUpdateScheme, StoreStaffFilter]):
    def __init__(self, request:Request):
        super(StoreStaffService, self).__init__(request, StoreStaff,StoreStaffCreateScheme, StoreStaffUpdateScheme)

    @permit('store_staff_update')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Row:
        return await super(StoreStaffService, self).update(id, obj)

    @permit('store_staff_list')
    async def list(self, _filter: FilterSchemaType, size: int = None):
        return await super(StoreStaffService, self).list(_filter, size)

    @permit('store_staff_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(StoreStaffService, self).create(obj)

    @permit('store_staff_delete')
    async def delete(self, id: Any) -> bool:
        return await super(StoreStaffService, self).delete(id)


    @permit('store_assign')
    async def company_change(self, store_id: UUID, user_id: UUID, commit=True) -> ModelType:
        store_staff = await self.get(user_id)
        if not store_staff:
            await self.create(StoreStaffCreateScheme(
                store_id=store_id, user_id=user_id
            ))
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        await self.send_relogin(user.id)
        return user