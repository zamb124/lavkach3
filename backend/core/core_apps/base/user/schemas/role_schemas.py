from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4

from ...user.models.role_models import Role
from .....schemas import BaseFilter
from .....schemas.basic_schemes import BaseModel
from .....schemas.list_schema import GenericListSchema
from .....schemas.timestamps import TimeStampScheme


class RoleBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: Optional[str] = None
    permission_allow_list: Optional[List[str]] = None
    permission_deny_list: Optional[List[str]] = None

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Role
        service = 'app.base.user.services.RoleService'

class RoleUpdateScheme(RoleBaseScheme):
    role_ids: Optional[List[UUID4]]
    title: Optional[str]


class RoleCreateScheme(RoleBaseScheme):
    title: str
    company_id: UUID4
    role_ids: Optional[List[UUID4]] = Field(title='Roles', model='role')


class RoleScheme(RoleCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        from_attributes = True


class RoleFilter(BaseFilter):
    title__in: Optional[List[str]] = Field(alias="title", default=None)
    permission_allow_list__contains: Optional[str] = Field(alias="permissions_allow", default=None)
    permission_deny_list__contains: Optional[str] = Field(alias="permissions_deny", default=None)
    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Role
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "permissions_allow", "permissions_deny"]


class RoleListSchema(GenericListSchema):
    data: Optional[List[RoleScheme]]


class PermissionSchema(BaseModel):
    lsn: int
    title: str
    description: Optional[str]


class PermissionListSchema(GenericListSchema):
    data: List[PermissionSchema] = []
