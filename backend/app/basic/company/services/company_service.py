from app.basic.company.models.company_models import Company
from app.basic.company.schemas.company_schemas import CompanyCreateScheme, CompanyUpdateScheme
from core.db.session import session, get_async_session
from core.service.base import BaseService
from fastapi import Depends


class CompanyService(BaseService[Company, CompanyCreateScheme, CompanyUpdateScheme]):
    def __init__(self, db_session=session):
        super(CompanyService, self).__init__(Company, db_session)


