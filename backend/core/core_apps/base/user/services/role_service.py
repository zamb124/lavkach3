from typing import Any, Optional

from starlette.requests import Request

from ....base.user.models.role_models import Role
from ....base.user.schemas.role_schemas import RoleCreateScheme, RoleUpdateScheme, RoleFilter
from .....permissions import permit, permits
from .....service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class RoleService(BaseService[Role, RoleCreateScheme, RoleUpdateScheme, RoleFilter]):
    def __init__(self, request: Request):
        super(RoleService, self).__init__(request, Role,  RoleCreateScheme, RoleUpdateScheme)

    @permit('role_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(RoleService, self).update(id, obj)

    @permit('role_list')
    async def list(self, _filter: FilterSchemaType, size: int=999):
        return await super(RoleService, self).list(_filter, size)

    @permit('role_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(RoleService, self).create(obj)

    @permit('role_delete')
    async def delete(self, id: Any) -> None:
        return await super(RoleService, self).delete(id)

    @permit('role_create')
    async def create_company_admin_role(self, company_id, commit=False) -> ModelType:
        obj = RoleCreateScheme(title='company_admin', company_id=company_id, permissions_allow=list(permits.keys()))
        return await super(RoleService, self).create(obj, commit)