from datetime import datetime

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List

from app.basic.user.models.role_models import Role
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class RoleBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: Optional[str] = None
    permission_allow_list: Optional[List[str]] = None
    permission_deny_list: Optional[List[str]] = None


class RoleUpdateScheme(RoleBaseScheme):
    role_ids: Optional[List[UUID4]]
    title: Optional[str]


class RoleCreateScheme(RoleBaseScheme):
    title: str
    company_id: UUID4
    role_ids: Optional[List[UUID4]] = None


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
