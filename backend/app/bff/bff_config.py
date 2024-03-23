import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig

from app.basic.company.schemas import CompanyUpdateScheme, CompanyCreateScheme, CompanyScheme, CompanyFilter
from app.basic.store.schemas import StoreScheme, StoreCreateScheme, StoreUpdateScheme
from app.bff.adapters.basic_adapter import BasicAdapter
from app.bff.apps.inventory import InventoryAdapter
from app.inventory.order.schemas import OrderUpdateScheme, OrderCreateScheme, OrderScheme
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
            'DOMAIN': '127.0.0.1',
            'PORT': '8001',
            'adapter': BasicAdapter,
            'schema': {
                'store': {
                    'base': StoreScheme,
                    'create': StoreCreateScheme,
                    'update': StoreUpdateScheme,
                },
                'company': {
                    'base': CompanyScheme,
                    'create': CompanyCreateScheme,
                    'update': CompanyUpdateScheme,
                    'filter': CompanyFilter,
                }
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
                },
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
