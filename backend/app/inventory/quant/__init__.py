from app.inventory.quant.models import Quant, Lot
from app.inventory.quant.schemas import QuantCreateScheme, QuantUpdateScheme, QuantFilter, QuantScheme, LotCreateScheme, \
    LotUpdateScheme, LotFilter, LotScheme

from app.inventory.quant.services import QuantService, LotService

__domain__ = {
    'quant': {
        'service': QuantService,
        'model': Quant,
        'schemas': {
            'create': QuantCreateScheme,
            'update': QuantUpdateScheme,
            'filter': QuantFilter,
            'get': QuantScheme
        }
    },
    'lot': {
        'service': LotService,
        'model': Lot,
        'schemas': {
            'create': LotCreateScheme,
            'update': LotUpdateScheme,
            'filter': LotFilter,
            'get': LotScheme
        }
    }
}
__all__ = ['__domain__']
