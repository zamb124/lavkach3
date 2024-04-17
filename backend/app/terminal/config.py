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

def get_config():
    env = os.getenv("ENV", "local")
    config_type = {
        "local": Config(),
    }
    return config_type[env]


config: Config = get_config()
