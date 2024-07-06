from starlette.requests import Request

from app.basic.company.models.company_models import Company
from app.basic.company.schemas.company_schemas import CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter
from core.permissions.permissions import permit
from core.service.base import BaseService, CreateSchemaType, ModelType


class CompanyService(BaseService[Company, CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter]):
    def __init__(self, request=Request):
        super(CompanyService, self).__init__(request, Company, CompanyCreateScheme, CompanyUpdateScheme)

    @permit('company_create', 'company_edit')
    async def create(self, obj: CreateSchemaType, commit=True) -> ModelType:
        return await super(CompanyService, self).create(obj, commit)


