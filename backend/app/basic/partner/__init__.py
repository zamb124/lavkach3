from core.helpers.cache import CacheStrategy
from .services import PartnerService
from .models import Partner
from .schemas.partner_schemas import PartnerCreateScheme, PartnerUpdateScheme, PartnerFilter, PartnerScheme

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
