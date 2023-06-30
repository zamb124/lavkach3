from pydantic import BaseModel, Field, UUID4
from pydantic.types import Optional, List
from app.basic.user.models.user_models import UserType
from app.basic.company.schemas import CompanyScheme
from core.types.types import *
from pydantic import BaseModel, Field, UUID4
from core.schemas.timestamps import TimeStampScheme
from app.basic.user.schemas.user_schemas import UserScheme
from core.schemas.list_schema import BaseListSchame


class RoleBaseScheme(BaseModel):
    vars: Optional[dict]
    title: str
    permissions_allow: Optional[List[str]]
    permissions_deny: Optional[List[str]]


class RoleUpdateScheme(RoleBaseScheme):
    pass


class RoleCreateScheme(RoleBaseScheme):
    company_id: UUID4


class RoleScheme(RoleCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        orm_mode = True


class RoleListSchema(BaseListSchame):
    data: List[RoleScheme] = []


class PermissionSchema(BaseModel):
    lsn: int
    title: str
    description: Optional[str]


class PermissionListSchema(BaseListSchame):
    data: List[PermissionSchema] = []
