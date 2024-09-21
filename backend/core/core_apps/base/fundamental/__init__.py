from ....schemas import BaseFilter
from .base import *


__domain__ = {
    'locale': {
        'service': None,
        'model': None,
        'cache_strategy': None,
        'schemas': {
            'create': None,
            'update': None,
            'filter': BaseFilter,
            'get': None
        }
    },
    'country': {
        'service': None,
        'model': None,
        'cache_strategy': None,
        'schemas': {
            'create': None,
            'update': None,
            'filter': BaseFilter,
            'get': None
        }
    },
    'currency': {
        'service': None,
        'model': None,
        'cache_strategy': None,
        'schemas': {
            'create': None,
            'update': None,
            'filter': BaseFilter,
            'get': None
        }
    }
}
__all__ = ['__domain__']
