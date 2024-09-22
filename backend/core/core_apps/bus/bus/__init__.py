from core.helpers.cache import CacheStrategy
from .services import BusService
from .models import Bus
from .shemas.bus_schemas import BusCreateScheme, BusUpdateScheme, BusFilter, BusScheme

__domain__ = {
    'bus': {
        'service': BusService,
        'model': Bus,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': BusCreateScheme,
            'update': BusUpdateScheme,
            'filter': BusFilter,
            'get': BusScheme
        }
    }
}

