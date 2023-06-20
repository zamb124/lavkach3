from celery import Celery
from core.config import config


celery_app = Celery('tasks', broker=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}')
