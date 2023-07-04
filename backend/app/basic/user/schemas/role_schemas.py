from datetime import datetime

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional, List

from app.basic.user.models.role_models import Role
from core.helpers.fastapi_filter_patch import BaseFilter
from core.schemas.list_schema import BaseListSchame, GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class RoleBaseScheme(BaseModel):
    vars: Optional[dict]
    title: Optional[str]
    permissions_allow: Optional[List[str]]
    permissions_deny: Optional[List[str]]


class RoleUpdateScheme(RoleBaseScheme):
    parents: Optional[List[UUID4]]
    title: Optional[str]


class RoleCreateScheme(RoleBaseScheme):
    title: str
    company_id: UUID4
    parents: Optional[List[UUID4]]


class RoleScheme(RoleCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        orm_mode = True


class RoleFilter(BaseFilter):
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id")
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created")
    created_at_lt: Optional[datetime] = Field(description="less created")
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated")
    updated_at_lt: Optional[datetime] = Field(description="less updated")
    company_id__in: Optional[List[str]] = Field(alias="company_id")
    title__in: Optional[List[str]] = Field(alias="title")
    permissions_allow__contains: Optional[str] = Field(alias="permissions_allow")
    permissions_deny__contains: Optional[str] = Field(alias="permissions_deny")
    order_by: Optional[List[str]]
    search: Optional[str]
    class Config:
        allow_population_by_field_name = True

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
