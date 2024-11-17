from core.helpers.cache import CacheStrategy
from .models import ProductStorageType
from .models.product_storage_models import StorageType
from .schemas import StorageTypeCreateScheme, StorageTypeUpdateScheme, StorageTypeFilter, StorageTypeScheme
from .schemas.product_storage_type_schemas import ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, \
    ProductStorageTypeFilter, ProductStorageTypeScheme
from .services import ProductStorageTypeService, StorageTypeService

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
    },
    'storage_type': {
        'service': StorageTypeService,
        'model': StorageType,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': StorageTypeCreateScheme,
            'update': StorageTypeUpdateScheme,
            'filter': StorageTypeFilter,
            'get': StorageTypeScheme
        }
    }
}

