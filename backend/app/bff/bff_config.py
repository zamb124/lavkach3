import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig

from app.basic.company.schemas import CompanyUpdateScheme, CompanyCreateScheme, CompanyScheme, CompanyFilter
from app.basic.partner.schemas import PartnerScheme, PartnerCreateScheme, PartnerUpdateScheme, PartnerFilter
from app.basic.product.schemas import ProductScheme, ProductCreateScheme, ProductUpdateScheme, ProductFilter, \
    ProductCategoryScheme, ProductCategoryCreateScheme, ProductCategoryUpdateScheme, ProductCategoryFilter, \
    ProductStorageTypeScheme, ProductStorageTypeCreateScheme, ProductStorageTypeUpdateScheme, ProductStorageTypeFilter
from app.basic.store.schemas import StoreScheme, StoreCreateScheme, StoreUpdateScheme, StoreFilter
from app.basic.uom.schemas import UomScheme, UomCreateScheme, UomUpdateScheme, UomFilter, UomCategoryScheme, \
    UomCategoryCreateScheme, UomCategoryUpdateScheme, UomCategoryFilter
from app.basic.user.schemas import UserScheme, UserCreateScheme, UserUpdateScheme, UserFilter, RoleScheme
from app.basic.user.schemas.role_schemas import RoleFilter, RoleUpdateScheme, RoleCreateScheme
from app.bff.adapters.basic_adapter import BasicAdapter
from app.bff.adapters.inventory_adapter import InventoryAdapter
from app.inventory.location.schemas import LocationScheme, LocationCreateScheme, LocationUpdateScheme, LocationFilter, \
    LocationTypeScheme, LocationTypeFilter, LocationTypeUpdateScheme, LocationTypeCreateScheme
from app.inventory.order.schemas import OrderUpdateScheme, OrderCreateScheme, OrderScheme, OrderFilter, OrderTypeFilter, \
    OrderTypeUpdateScheme, OrderTypeCreateScheme, OrderTypeScheme
from app.inventory.order.schemas.move_schemas import MoveScheme, MoveCreateScheme, MoveUpdateScheme, MoveFilter
from app.inventory.quant.schemas import LotScheme, LotCreateScheme, LotUpdateScheme, LotFilter
from core.config import Config as CoreConfig

BaseConfig.arbitrary_types_allowed = True
logging.basicConfig(level=logging.INFO)

load_dotenv()


def my_import(name):
    """
    Метод для удобного импорта адаптеров по пути
    """
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class Config(CoreConfig):
    services: dict = {
        'basic': {
            'DOMAIN': 'basic',
            'PORT': '8001',
            'adapter': BasicAdapter,
            'schema': {
                'store': {
                    'base': StoreScheme,
                    'create': StoreCreateScheme,
                    'update': StoreUpdateScheme,
                    'filter': StoreFilter,
                },
                'company': {
                    'base': CompanyScheme,
                    'create': CompanyCreateScheme,
                    'update': CompanyUpdateScheme,
                    'filter': CompanyFilter,
                },
                'partner': {
                    'base': PartnerScheme,
                    'create': PartnerCreateScheme,
                    'update': PartnerUpdateScheme,
                    'filter': PartnerFilter,
                },
                'product_category': {
                    'base': ProductCategoryScheme,
                    'create': ProductCategoryCreateScheme,
                    'update': ProductCategoryUpdateScheme,
                    'filter': ProductCategoryFilter,
                },
                'product_storage_type': {
                    'base': ProductStorageTypeScheme,
                    'create': ProductStorageTypeCreateScheme,
                    'update': ProductStorageTypeUpdateScheme,
                    'filter': ProductStorageTypeFilter,
                },
                'product': {
                    'base': ProductScheme,
                    'create': ProductCreateScheme,
                    'update': ProductUpdateScheme,
                    'filter': ProductFilter,
                },
                'uom_category': {
                    'base': UomCategoryScheme,
                    'create': UomCategoryCreateScheme,
                    'update': UomCategoryUpdateScheme,
                    'filter': UomCategoryFilter,
                },
                'uom': {
                    'base': UomScheme,
                    'create': UomCreateScheme,
                    'update': UomUpdateScheme,
                    'filter': UomFilter,
                },
                'user': {
                    'base': UserScheme,
                    'create': UserCreateScheme,
                    'update': UserUpdateScheme,
                    'filter': UserFilter,
                },
                'role': {
                    'base': RoleScheme,
                    'create': RoleCreateScheme,
                    'update': RoleUpdateScheme,
                    'filter': RoleFilter,
                },
            }
        },
        'inventory': {
            'DOMAIN': '127.0.0.1',
            'PORT': '8002',
            'adapter': InventoryAdapter,
            'schema': {
                'order': {
                    'base': OrderScheme,
                    'create': OrderCreateScheme,
                    'update': OrderUpdateScheme,
                    'filter': OrderFilter,
                    'sort': ['number', 'planned_datetime']
                },
                'order_type': {
                    'base': OrderTypeScheme,
                    'create': OrderTypeCreateScheme,
                    'update': OrderTypeUpdateScheme,
                    'filter': OrderTypeFilter,
                },
                'move': {
                    'base': MoveScheme,
                    'create': MoveCreateScheme,
                    'update': MoveUpdateScheme,
                    'filter': MoveFilter,
                },
                'lot': {
                    'base': LotScheme,
                    'create': LotCreateScheme,
                    'update': LotUpdateScheme,
                    'filter': LotFilter,
                },
                'location': {
                    'base': LocationScheme,
                    'create': LocationCreateScheme,
                    'update': LocationUpdateScheme,
                    'filter': LocationFilter,
                },
                'location_type': {
                    'base': LocationTypeScheme,
                    'create': LocationTypeCreateScheme,
                    'update': LocationTypeUpdateScheme,
                    'filter': LocationTypeFilter,
                },
                # 'suggest': {
                #     'base': SuggestScheme,
                #     'create': SuggestScheme,
                #     'update': SuggestUpdateScheme,
                #     'filter': SuggestFilter,
                # },
            },
        }
    }


class DevelopmentConfig(Config):
    ...


class LocalConfig(Config):
    ...


class ProductionConfig(Config):
    ...


def get_config():
    env = os.getenv("ENV", "local")
    for name, value in os.environ.items():
        # logging.info("{0}: {1}".format(name, value))
        # print("{0}: {1}".format(name, value))
        pass
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
