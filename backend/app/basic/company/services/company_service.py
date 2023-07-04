from app.basic.company.models.company_models import Company
from app.basic.company.schemas.company_schemas import CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter
from core.db.session import session
from core.service.base import BaseService, CreateSchemaType, ModelType
from core.permissions.permissions import permit

Deny = 'Deny'

class CompanyService(BaseService[Company, CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter]):
    def __init__(self, request):
        super(CompanyService, self).__init__(request, Company)

    @permit('company_create', 'company_edit')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(CompanyService, self).create(obj)

