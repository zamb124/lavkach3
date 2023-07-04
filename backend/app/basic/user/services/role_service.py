from typing import List, Any, Optional

from app.basic.user.models.role_models import Role
from app.basic.user.schemas.role_schemas import RoleCreateScheme, RoleUpdateScheme, RoleFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class RoleService(BaseService[Role, RoleCreateScheme, RoleUpdateScheme, RoleFilter]):
    def __init__(self, request=None, db_session=session):
        super(RoleService, self).__init__(request, Role, db_session)

    @permit('role_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(RoleService, self).update(id, obj)

    @permit('role_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(RoleService, self).list(_filter, size)

    @permit('role_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(RoleService, self).create(obj)

    async def delete(self, id: Any) -> None:
        return await super(RoleService).delete(id)
