from typing import List

from app.basic.user.models.role_models import Role
from app.basic.user.schemas.role_schemas import RoleCreateScheme, RoleUpdateScheme, RoleFilter
from core.db.session import session
from core.service.base import BaseService


class RoleService(BaseService[Role, RoleCreateScheme, RoleUpdateScheme, RoleFilter]):
    def __init__(self, request=None, db_session=session):
        super(RoleService, self).__init__(request, Role, db_session)

