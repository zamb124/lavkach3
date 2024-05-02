from core.helpers.cache import CacheStrategy
from .services import UserService, RoleService
from .models import User, Role
from .schemas.user_schemas import UserCreateScheme, UserUpdateScheme, UserFilter, UserScheme
from .schemas.role_schemas import RoleCreateScheme, RoleUpdateScheme, RoleFilter, RoleScheme


__domain__ = {
    'user': {
        'service': UserService,
        'model': User,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': UserCreateScheme,
            'update': UserUpdateScheme,
            'filter': UserFilter,
            'get': UserScheme
        }
    },
    'role': {
        'service': RoleService,
        'model': Role,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': RoleCreateScheme,
            'update': RoleUpdateScheme,
            'filter': RoleFilter,
            'get': RoleScheme
        }
    }
}

