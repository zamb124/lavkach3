from .user_schemas import UserScheme, UserCreateScheme, UserUpdateScheme, BaseModel, GetUserListResponseSchema, \
    LoginResponseSchema, UserListSchema
from .role_schemas import RoleScheme, RoleCreateScheme, RoleUpdateScheme, RoleListSchema, PermissionListSchema, \
    PermissionSchema


class ExceptionResponseSchema(BaseModel):
    error: str
