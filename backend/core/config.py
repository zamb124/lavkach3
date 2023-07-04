import logging
import os

from dotenv import load_dotenv
from pydantic import BaseConfig
from pydantic import BaseSettings

BaseConfig.arbitrary_types_allowed = True
logging.basicConfig(level=logging.INFO)


load_dotenv()

class Config(BaseSettings):
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
    POSTGRES_TEST_DATABASE_URL: str = f'postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}/postgres'
    TEST_WRITER_DB_URL: str = f'postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}'
    WRITER_DB_URL: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    READER_DB_URL: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY") or 'secret'
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM") or 'HS256'
    SENTRY_SDN: str = os.environ.get("SENTRY_SDN") or None
    CELERY_BROKER_URL: str = "amqp://user:bitnami@localhost:5672/"
    CELERY_BACKEND_URL: str = "redis://:password123@localhost:6379/0"
    REDIS_HOST: str = os.environ.get("REDIS_HOST")
    REDIS_PORT: int = os.environ.get("REDIS_PORT")


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
