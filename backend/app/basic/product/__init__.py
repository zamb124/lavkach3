from core.helpers.cache import CacheStrategy
from .models import Product, ProductCategory
from .schemas.product_category_schemas import ProductCategoryCreateScheme, ProductCategoryUpdateScheme, \
    ProductCategoryFilter, ProductCategoryScheme
from .schemas.product_schemas import ProductCreateScheme, ProductUpdateScheme, ProductFilter, ProductScheme
from .services import ProductService, ProductCategoryService

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
}

