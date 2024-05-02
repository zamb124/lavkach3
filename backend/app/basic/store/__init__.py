from core.helpers.cache import CacheStrategy
from .services import StoreService
from .models import Store
from .schemas.store_schemas import StoreCreateScheme, StoreUpdateScheme, StoreFilter, StoreScheme

__domain__ = {
    'store': {
        'service': StoreService,
        'model': Store,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': StoreCreateScheme,
            'update': StoreUpdateScheme,
            'filter': StoreFilter,
            'get': StoreScheme
        }
    }
}

