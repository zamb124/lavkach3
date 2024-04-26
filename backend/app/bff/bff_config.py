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
from app.basic.user.schemas.role_schemas import *
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
            'DOMAIN': os.environ.get("BASIC_DOMAIN") or '127.0.0.1',
            'PORT': '8001',
        },
        'inventory': {
            'DOMAIN': os.environ.get("INVENTORY_DOMAIN") or '127.0.0.1',
            'PORT': '8002',
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
