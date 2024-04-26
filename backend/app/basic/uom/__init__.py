from .services import UomService, UomCategoryService
from .models import Uom, UomCategory
from .schemas.uom_schemas import UomCreateScheme, UomUpdateScheme, UomFilter, UomScheme
from .schemas.uom_category_schemas import UomCategoryCreateScheme, UomCategoryUpdateScheme, UomCategoryFilter, UomCategoryScheme

__domain__ = {
    'uom': {
        'service': UomService,
        'model': Uom,
        'schemas': {
            'create': UomCreateScheme,
            'update': UomUpdateScheme,
            'filter': UomFilter,
            'get': UomScheme
        }
    },
    'uom_category': {
        'service': UomCategoryService,
        'model': UomCategory,
        'schemas': {
            'create': UomCategoryCreateScheme,
            'update': UomCategoryUpdateScheme,
            'filter': UomCategoryFilter,
            'get': UomCategoryScheme
        }
    }
}

