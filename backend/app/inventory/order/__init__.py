from app.inventory.order.models import Move, Order, OrderType, Suggest
from app.inventory.order.schemas import OrderCreateScheme, OrderUpdateScheme, OrderFilter, OrderScheme, \
    OrderTypeCreateScheme, OrderTypeUpdateScheme, OrderTypeFilter, OrderTypeScheme
from app.inventory.order.schemas.move_schemas import MoveCreateScheme, MoveUpdateScheme, MoveFilter, MoveScheme
from app.inventory.order.schemas.suggest_schemas import SuggestScheme, SuggestFilter, SuggestUpdateScheme, \
    SuggestCreateScheme
from app.inventory.order.services import MoveService, OrderService, OrderTypeService, SuggestService

__domain__ = {
    'move': {
        'service': MoveService,
        'model': Move,
        'schemas': {
            'create': MoveCreateScheme,
            'update': MoveUpdateScheme,
            'filter': MoveFilter,
            'get': MoveScheme
        }
    },
    'order': {
        'service': OrderService,
        'model': Order,
        'schemas': {
            'create': OrderCreateScheme,
            'update': OrderUpdateScheme,
            'filter': OrderFilter,
            'get': OrderScheme
        }
    },
    'order_type': {
        'service': OrderTypeService,
        'model': OrderType,
        'schemas': {
            'create': OrderTypeCreateScheme,
            'update': OrderTypeUpdateScheme,
            'filter': OrderTypeFilter,
            'get': OrderTypeScheme
        }
    },
    'suggest': {
        'service': SuggestService,
        'model': Suggest,
        'schemas': {
            'create': SuggestCreateScheme,
            'update': SuggestUpdateScheme,
            'filter': SuggestFilter,
            'get': SuggestScheme
        }
    }

}
__all__ = ['__domain__']
