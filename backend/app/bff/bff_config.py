import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig
from core.config import Config as CoreConfig
BaseConfig.arbitrary_types_allowed = True
logging.basicConfig(level=logging.INFO)


load_dotenv()

class Config(CoreConfig):
    services: dict = {
        'basic': {
            'DOMAIN': '127.0.0.1',
            'PORT': '8001'
        },
        'inventory': {
            'DOMAIN': '127.0.0.1',
            'PORT': '8002'
        },

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
        #logging.info("{0}: {1}".format(name, value))
        #print("{0}: {1}".format(name, value))
        pass
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
