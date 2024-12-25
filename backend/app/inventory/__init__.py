
from core.helpers.cache import CacheStrategy
from app.inventory.inventory_adapter import InventoryAdapter
from app.inventory.location.models import Location, LocationType
from app.inventory.location.schemas import LocationScheme, LocationCreateScheme, LocationUpdateScheme, LocationFilter
from app.inventory.location.schemas import LocationTypeScheme, LocationTypeCreateScheme, LocationTypeUpdateScheme, \
    LocationTypeFilter
from app.inventory.location.services import LocationService, LocationTypeService
from app.inventory.order.models import Move, MoveType, Order, OrderType, Suggest, MoveLog
from app.inventory.order.schemas import MoveLogScheme, MoveLogCreateScheme, MoveLogUpdateScheme, MoveLogFilter
from app.inventory.order.schemas import MoveScheme, MoveCreateScheme, MoveUpdateScheme, MoveFilter
from app.inventory.order.schemas import OrderScheme, OrderCreateScheme, OrderUpdateScheme, OrderFilter
from app.inventory.order.schemas import OrderTypeScheme, OrderTypeCreateScheme, OrderTypeUpdateScheme, OrderTypeFilter
from app.inventory.order.schemas import SuggestScheme, SuggestCreateScheme, SuggestUpdateScheme, SuggestFilter
from app.inventory.order.services import MoveService, OrderService, OrderTypeService, SuggestService, MoveLogService
from app.inventory.product_storage.models import ProductStorageType, StorageType
from app.inventory.product_storage.schemas import ProductStorageTypeScheme, ProductStorageTypeCreateScheme, \
    ProductStorageTypeUpdateScheme, ProductStorageTypeFilter
from app.inventory.product_storage.schemas import StorageTypeScheme, StorageTypeCreateScheme, StorageTypeUpdateScheme, \
    StorageTypeFilter
from app.inventory.product_storage.services import ProductStorageTypeService, StorageTypeService
from app.inventory.quant.models import Quant, Lot
from app.inventory.quant.schemas import LotScheme, LotCreateScheme, LotUpdateScheme, LotFilter
from app.inventory.quant.schemas import QuantScheme, QuantCreateScheme, QuantUpdateScheme, QuantFilter
from app.inventory.quant.services import QuantService, LotService
from app.inventory.store_staff.models import StoreStaff
from app.inventory.store_staff.schemas import StoreStaffScheme, StoreStaffCreateScheme, StoreStaffUpdateScheme, \
    StoreStaffFilter
from app.inventory.store_staff.services import StoreStaffService

__inventory_manifest__ = {
    'name': 'inventory',
    'adapter': InventoryAdapter,
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
    },
    'move_log': {
        'service': MoveLogService,
        'model': MoveLog,
        'schemas': {
            'create': MoveLogCreateScheme,
            'update': MoveLogUpdateScheme,
            'filter': MoveLogFilter,
            'get': MoveLogScheme
        }
    },
    'location': {
        'service': LocationService,
        'model': Location,
        'schemas': {
            'create': LocationCreateScheme,
            'update': LocationUpdateScheme,
            'filter': LocationFilter,
            'get': LocationScheme
        }
    },
    'location_type': {
        'service': LocationTypeService,
        'model': LocationType,
        'schemas': {
            'create': LocationTypeCreateScheme,
            'update': LocationTypeUpdateScheme,
            'filter': LocationTypeFilter,
            'get': LocationTypeScheme
        }
    },
    'quant': {
        'service': QuantService,
        'model': Quant,
        'schemas': {
            'create': QuantCreateScheme,
            'update': QuantUpdateScheme,
            'filter': QuantFilter,
            'get': QuantScheme
        }
    },
    'lot': {
        'service': LotService,
        'model': Lot,
        'schemas': {
            'create': LotCreateScheme,
            'update': LotUpdateScheme,
            'filter': LotFilter,
            'get': LotScheme
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
    },
    'store_staff': {
        'service': StoreStaffService,
        'model': StoreStaff,
        'schemas': {
            'create': StoreStaffCreateScheme,
            'update': StoreStaffUpdateScheme,
            'filter': StoreStaffFilter,
            'get': StoreStaffScheme
        }
    },

}



