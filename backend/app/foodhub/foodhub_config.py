import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig

from core.service_config import Config as CoreConfig

BaseConfig.arbitrary_types_allowed = True
logging.basicConfig(level=logging.INFO)

load_dotenv()


class Config(CoreConfig):
    BROKER_PATH: str = 'app.foodhub.prescription_server:app'
    APP_HOST: str = os.environ.get("PRESCRIPTION_HOST") or os.environ.get("APP_HOST") or '127.0.0.1'
    APP_PORT: int = os.environ.get("PRESCRIPTION_PORT") or os.environ.get("APP_PORT") or '8004'
    APP_PROTOCOL: str = os.environ.get('PRESCRIPTION_PROTOCOL') or os.environ.get('APP_PROTOCOL') or 'http'


class DevelopmentConfig(Config):
    ...

class DockerConfig(Config):
    APP_HOST: str = 'prescription_app'
    APP_PORT: int = '80'

class LocalConfig(Config):
    ...
class TestConfig(Config):
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
        "test": TestConfig(),
        "docker": DockerConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
