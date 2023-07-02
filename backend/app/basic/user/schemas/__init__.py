from .user_schemas import UserScheme, UserCreateScheme, UserUpdateScheme, BaseModel, GetUserListResponseSchema, \
    LoginResponseSchema, UserFilter, UserListSchema
from .role_schemas import RoleScheme, RoleCreateScheme, RoleUpdateScheme, PermissionListSchema, \
    PermissionSchema


class ExceptionResponseSchema(BaseModel):
    error: str
