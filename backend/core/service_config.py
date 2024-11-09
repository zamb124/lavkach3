import logging
import os

from pydantic import BaseConfig
from pydantic_settings import BaseSettings

BaseConfig.arbitrary_types_allowed = True
logging.basicConfig(level=logging.INFO)


class Config(BaseSettings):
    APP_HOST: str = os.environ.get("APP_HOST") or 'localhost'
    APP_PORT: int = os.environ.get("APP_PORT") or '8000'
    APP_PROTOCOL: str = os.environ.get('APP_PROTOCOL') or 'http'
    BUS_HOST: str = os.environ.get('BUS_HOST') or '127.0.0.1'
    BUS_PORT: str = os.environ.get('BUS_PORT') or '8099'
    INTERCO_TOKEN: str = os.environ.get('INTERCO_TOKEN') or 'netu'


class DevelopmentConfig(Config):
    ...


class DockerConfig(Config):
    BUS_HOST: str = 'bus_app'
    BUS_PORT: str = '80'


class LocalConfig(Config):
    ...


class TestConfig(Config):
    ...


class ProductionConfig(Config):
    ...


class ModuleEnv:
    ...


def my_import(name):
    """
    Метод для удобного импорта адаптеров по пути
    """
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def get_config():
    env = os.getenv("ENV", "local")
    for name, value in os.environ.items():
        logging.info("{0}: {1}".format(name, value))
        # print("{0}: {1}".format(name, value))
        pass
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "test": LocalConfig(),
        "docker": DockerConfig(),
        "prod": ProductionConfig(),
    }
    config = config_type[env]
    return config


config: Config = get_config()
