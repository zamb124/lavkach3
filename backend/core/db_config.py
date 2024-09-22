import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig
from pydantic_settings import BaseSettings

BaseConfig.arbitrary_types_allowed = True
logging.basicConfig(level=logging.INFO)
cwd = os.getcwd()
env_path = os.path.join(cwd, os.environ.get('DOTENV_PATH') or '.env')
load_dotenv(env_path)


class Config(BaseSettings):
    BROKER_PATH: str = 'false'
    ENV: str = os.environ.get("ENV") or 'local'
    DEBUG: bool = os.environ.get("DEBUG") or True
    APP_HOST: str = os.environ.get("APP_HOST") or 'localhost'
    APP_PORT: int = os.environ.get("APP_PORT") or '8000'
    DB_HOST: str = os.environ.get("DB_HOST") or 'localhost'
    DB_HOST_TEST: str = os.environ.get("DB_TEST") or 'localhost'
    DB_PORT: str = os.environ.get("DB_PORT") or '5432'
    DB_PORT_TEST: str = os.environ.get("DB_PORT_TEST") or '5432'
    DB_NAME: str = os.environ.get("DB_NAME") or 'lavkach'
    DB_NAME_TEST: str = os.environ.get("DB_NAME_TEST") or 'lavkach2'
    DB_USER: str = os.environ.get("DB_USER") or 'taxi'
    DB_USER_TEST: str = os.environ.get("DB_USER_TEST") or 'taxi'
    DB_PASS: str = os.environ.get("DB_PASS") or 'test'
    DB_PASS_TEST: str = os.environ.get("DB_PASS_TEST") or 'test'
    DB_SSL: str = os.environ.get('DB_SSL') or 'prefer'
    POSTGRES_TEST_DATABASE_URL: str = f'postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}/postgres'
    TEST_WRITER_DB_URL: str = f'postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}'
    WRITER_DB_URL: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl={DB_SSL}'
    READER_DB_URL: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl={DB_SSL}'
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY") or 'secret'
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM") or 'HS256'
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
    SUPERUSER_EMAIL: str = os.environ.get('SUPERUSER_EMAIL') or ''
    SUPERUSER_PASSWORD: str = os.environ.get('SUPERUSER_PASSWORD') or ''
    BASE_HOST: str = os.environ.get('BASIC_HOST') or '127.0.0.1'
    BASE_PORT: str = os.environ.get('BASIC_PORT') or '8888'
    BUS_HOST: str = os.environ.get('BUS_HOST') or '127.0.0.1'
    BUS_PORT: str = os.environ.get('BUS_PORT') or '8099'
    INTERCO_TOKEN: str = os.environ.get('INTERCO_TOKEN') or 'netu'


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
        pass
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
