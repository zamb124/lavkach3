from aio_celery import Celery
from core.db_config import config


#celery_app = Celery('tasks', broker=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}')
