from core.helpers.cache import CacheStrategy
from .services import ProductStorageTypeService
from .models import ProductStorageType
from .schemas.product_storage_type_schemas import ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, ProductStorageTypeFilter, ProductStorageTypeScheme


__domain__ = {
    'product_storage_type': {
        'service': ProductStorageTypeService,
        'model': ProductStorageType,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': ProductStorageTypeCreateScheme,
            'update': ProductStorageTypeUpdateScheme,
            'filter': ProductStorageTypeFilter,
            'get': ProductStorageTypeScheme
        }
    }
}

