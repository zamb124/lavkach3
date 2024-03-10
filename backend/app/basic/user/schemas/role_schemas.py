from datetime import datetime

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4
from typing import Optional, List

from app.basic.user.models.role_models import Role
from core.helpers.fastapi_filter_patch import BaseFilter
from core.schemas.list_schema import BaseListSchame, GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class RoleBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: Optional[str] = None
    permissions_allow: Optional[List[str]] = None
    permissions_deny: Optional[List[str]] = None


class RoleUpdateScheme(RoleBaseScheme):
    parents: Optional[List[UUID4]]
    title: Optional[str]


class RoleCreateScheme(RoleBaseScheme):
    title: str
    company_id: UUID4
    parents: Optional[List[UUID4]] = None


class RoleScheme(RoleCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        orm_mode = True


class RoleFilter(BaseFilter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[str]] = Field(alias="company_id", default=None)
    title__in: Optional[List[str]] = Field(alias="title", default=None)
    permissions_allow__contains: Optional[str] = Field(alias="permissions_allow", default=None)
    permissions_deny__contains: Optional[str] = Field(alias="permissions_deny", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str] = None
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


class PermissionListSchema(BaseListSchame):
    data: List[PermissionSchema] = []
