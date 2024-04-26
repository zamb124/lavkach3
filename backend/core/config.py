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
    DEBUG: bool = os.environ.get("DEBUG") or True
    CELERY_BROKER_URL: str = "amqp://user:bitnami@localhost:5672/"
    CELERY_BACKEND_URL: str = "redis://:password123@localhost:5370/0"
    REDIS_HOST: str = os.environ.get("REDIS_HOST") or 'localhost'
    REDIS_PORT: int = os.environ.get("REDIS_PORT") or '5370'
    REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD") or ''
    REDIS_SSL: bool = os.environ.get("REDIS_SSL") or False
    REDIS_CERT_PATH: str = os.environ.get("REDIS_CERT_PATH") or ''
    AWS_DEFAULT_REGION: str = os.environ.get("AWS_DEFAULT_REGION") or 'us-east-1'
    AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID") or ''
    AWS_SECRET_ACCESS_KEY: str = os.environ.get("AWS_SECRET_ACCESS_KEY") or ''
    AWS_DEFAULT_BUCKET: str = os.environ.get("AWS_DEFAULT_BUCKET") or 'us-east-1'
    AWS_ENDPOINT_URL: str = os.environ.get("AWS_ENDPOINT_URL") or 'https://storage.yandexcloud.net'
    SUPERUSER_EMAIL: str = os.environ.get("SUPERUSER_EMAIL") or ''
    SUPERUSER_PASSWORD: str = os.environ.get("SUPERUSER_PASSWORD") or ''


class DevelopmentConfig(Config):
    ...


class LocalConfig(Config):
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
        print("{0}: {1}".format(name, value))
        pass
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    config =  config_type[env]
    return config

config: Config = get_config()


