from app.company.models.company import Company
from app.company.schemas.company import CompanyCreateScheme, CompanyUpdateScheme
from core.db.session import session
from core.service.base import BaseService


class CompanyService(BaseService[Company, CompanyCreateScheme, CompanyUpdateScheme]):
    def __init__(self, db_session: session=session):
        super(CompanyService, self).__init__(Company, db_session)


