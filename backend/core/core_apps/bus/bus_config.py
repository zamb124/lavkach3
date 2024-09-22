import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig

from ...service_config import Config as CoreConfig

BaseConfig.arbitrary_types_allowed = True
logging.basicConfig(level=logging.INFO)

load_dotenv()


class Config(CoreConfig):
    BROKER_PATH: str = 'app.bus.bus_server:app'
    APP_HOST: str = os.environ.get("BUS_HOST") or os.environ.get("APP_HOST") or '127.0.0.1'
    APP_PORT: int = os.environ.get("BUS_PORT") or os.environ.get("APP_PORT") or '8099'
    APP_PROTOCOL: str = os.environ.get('BUS_PROTOCOL') or os.environ.get('APP_PROTOCOL') or 'http'
    BASIC_HOST: str = os.environ.get('BASIC_HOST') or '127.0.0.1'
    BASIC_PORT: str = os.environ.get('BASIC_PORT') or '8001'


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
