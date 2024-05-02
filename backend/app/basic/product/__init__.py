from core.helpers.cache import CacheStrategy
from .services import ProductService, ProductCategoryService, ProductStorageTypeService
from .models import Product, ProductCategory, ProductStorageType
from .schemas.product_schemas import ProductCreateScheme, ProductUpdateScheme, ProductFilter, ProductScheme
from .schemas.product_category_schemas import ProductCategoryCreateScheme, ProductCategoryUpdateScheme, \
    ProductCategoryFilter, ProductCategoryScheme
from .schemas.product_storage_type_schemas import ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, ProductStorageTypeFilter, ProductStorageTypeScheme


__domain__ = {
    'product': {
        'service': ProductService,
        'model': Product,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': ProductCreateScheme,
            'update': ProductUpdateScheme,
            'filter': ProductFilter,
            'get': ProductScheme
        }
    },
    'product_category': {
        'service': ProductCategoryService,
        'model': ProductCategory,
        'cache_strategy': CacheStrategy.FULL,
        'schemas': {
            'create': ProductCategoryCreateScheme,
            'update': ProductCategoryUpdateScheme,
            'filter': ProductCategoryFilter,
            'get': ProductCategoryScheme
        }
    },
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

