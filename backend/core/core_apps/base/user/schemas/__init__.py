from .role_schemas import RoleScheme, RoleCreateScheme, RoleUpdateScheme, PermissionListSchema, \
    PermissionSchema
from .user_schemas import UserScheme, UserCreateScheme, UserUpdateScheme, BaseModel, \
    LoginResponseSchema, UserFilter, UserListSchema


class ExceptionResponseSchema(BaseModel):
    error: str
