from app.basic.user.models.role_models import Role
from app.basic.user.schemas.role_schemas import RoleCreateScheme, RoleUpdateScheme
from core.db.session import session
from core.service.base import BaseService


class RoleService(BaseService[Role, RoleCreateScheme, RoleUpdateScheme]):
    def __init__(self, request, db_session=session):
        super(RoleService, self).__init__(request, Role, db_session)
