from core.helpers.cache import CacheStrategy
from .models import Store
from .schemas.store_schemas import StoreCreateScheme, StoreUpdateScheme, StoreFilter, StoreScheme
from .services import StoreService

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

