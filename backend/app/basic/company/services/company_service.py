from app.basic.company.models.company_models import Company
from app.basic.company.schemas.company_schemas import CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter
from core.db.session import session, get_async_session
from core.service.base import BaseService

Deny = 'Deny'

class CompanyService(BaseService[Company, CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter]):
    def __init__(self, request, db_session=session):
        super(CompanyService, self).__init__(request, Company, db_session)


