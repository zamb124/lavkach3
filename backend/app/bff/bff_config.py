import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig

from core.db_config import Config as CoreConfig

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
        'bus': {
            'DOMAIN': f'{os.environ.get("BUS_DOMAIN")}' or '127.0.0.1',
            'PORT': '8099',
        },
        'basic': {
            'DOMAIN': f'http://{os.environ.get("BASIC_DOMAIN")}' or '127.0.0.1',
            'PORT': '8001',
        },
        'inventory': {
            'DOMAIN': f'http://{os.environ.get("INVENTORY_DOMAIN")}' or '127.0.0.1',
            'PORT': '8002',
        }
    }
    css_engine:str = '1tailwind'


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
