from .services import PartnerService
from .models import Partner
from .schemas.partner_schemas import PartnerCreateScheme, PartnerUpdateScheme, PartnerFilter, PartnerScheme

__domain__ = {
    'partner': {
        'service': PartnerService,
        'model': Partner,
        'schemas': {
            'create': PartnerCreateScheme,
            'update': PartnerUpdateScheme,
            'filter': PartnerFilter,
            'get': PartnerScheme
        }
    }
}
