import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig
from pydantic_settings import BaseSettings

BaseConfig.arbitrary_types_allowed = True
logging.basicConfig(level=logging.INFO)

load_dotenv()


class Config(BaseSettings):
    ENV: str = os.environ.get("ENV") or 'local'
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY") or 'secret'
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM") or 'HS256'


class DevelopmentConfig(Config):
    ...


class LocalConfig(Config):
    ...


class ProductionConfig(Config):
    ...


class ModuleEnv:
    ...


def get_config():
    env = os.getenv("ENV", "local")
    for name, value in os.environ.items():
        logging.info("{0}: {1}".format(name, value))
        print("{0}: {1}".format(name, value))
        pass
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
