from core.helpers.cache import CacheStrategy
from .models import Partner
from .schemas.partner_schemas import PartnerCreateScheme, PartnerUpdateScheme, PartnerFilter, PartnerScheme
from .services import PartnerService

__domain__ = {
    'partner': {
        'service': PartnerService,
        'model': Partner,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': PartnerCreateScheme,
            'update': PartnerUpdateScheme,
            'filter': PartnerFilter,
            'get': PartnerScheme
        }
    }
}
