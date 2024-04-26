from app.basic.company.models import Company
from app.basic.company.schemas import CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter, CompanyScheme
from app.basic.company.services import CompanyService

__domain__ = {
    'company': {
        'service': CompanyService,
        'model': Company,
        'schemas': {
            'create': CompanyCreateScheme,
            'update': CompanyUpdateScheme,
            'filter': CompanyFilter,
            'get': CompanyScheme
        }
    }
}
__all__ = ['__domain__']

