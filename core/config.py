import logging
import os

from pydantic import BaseSettings
import logging
logging.basicConfig(level=logging.INFO)

class Config(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8085
    WRITER_DB_URL: str = f"postgresql+asyncpg://taxi:test@localhost:5432/fastapi"
    READER_DB_URL: str = f"postgresql+asyncpg://taxi:test@localhost:5432/fastapi"
    JWT_SECRET_KEY: str = "fastapi"
    JWT_ALGORITHM: str = "HS256"
    SENTRY_SDN: str = None
    CELERY_BROKER_URL: str = "amqp://user:bitnami@localhost:5672/"
    CELERY_BACKEND_URL: str = "redis://:password123@localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379


class DevelopmentConfig(Config):
    WRITER_DB_URL: str = f"postgresql+asyncpg://zambas:Angel-15111990@rc1b-gsgkmvrv04yanye2.mdb.yandexcloud.net:6432/lavkach"
    READER_DB_URL: str = f"postgresql+asyncpg://zambas:Angel-15111990@rc1b-gsgkmvrv04yanye2.mdb.yandexcloud.net:6432/lavkach"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


class LocalConfig(Config):
    WRITER_DB_URL: str = f"postgresql+asyncpg://zambas:Angel-15111990@rc1b-gsgkmvrv04yanye2.mdb.yandexcloud.net:6432/lavkach"
    READER_DB_URL: str = f"postgresql+asyncpg://zambas:Angel-15111990@rc1b-gsgkmvrv04yanye2.mdb.yandexcloud.net:6432/lavkach"


class ProductionConfig(Config):
    DEBUG: str = False
    WRITER_DB_URL: str = f"postgresql+asyncpg://zambas:Angel-15111990@rc1b-gsgkmvrv04yanye2.mdb.yandexcloud.net:6432/lavkach"
    READER_DB_URL: str = f"postgresql+asyncpg://zambas:Angel-15111990@rc1b-gsgkmvrv04yanye2.mdb.yandexcloud.net:6432/lavkach"


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
