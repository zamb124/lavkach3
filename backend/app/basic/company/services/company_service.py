from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.basic.company.models.company_models import Company
from app.basic.company.schemas.company_schemas import CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter
from core.db.session import session
from core.service.base import BaseService, CreateSchemaType, ModelType
from core.permissions.permissions import permit


class CompanyService(BaseService[Company, CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter]):
    def __init__(self, request=None, db_session=None):
        super(CompanyService, self).__init__(request, Company, db_session)

    @permit('company_create', 'company_edit')
    async def create(self, obj: CreateSchemaType, commit=True) -> ModelType:
        return await super(CompanyService, self).create(obj, commit)


