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
        'schemas': {
            'create': ProductStorageTypeCreateScheme,
            'update': ProductStorageTypeUpdateScheme,
            'filter': ProductStorageTypeFilter,
            'get': ProductStorageTypeScheme
        }
    }
}

