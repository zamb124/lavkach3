from core.helpers.cache import CacheStrategy
from .models import Company
from .schemas import CompanyCreateScheme, CompanyUpdateScheme, CompanyFilter, CompanyScheme
from .services import CompanyService

__domain__ = {
    'company': {
        'service': CompanyService,
        'model': Company,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': CompanyCreateScheme,
            'update': CompanyUpdateScheme,
            'filter': CompanyFilter,
            'get': CompanyScheme
        }
    }
}
__all__ = ['__domain__']



