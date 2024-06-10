from core.fastapi.adapters import BaseAdapter
from app.basic.basic_config import config

class BasicAdapter(BaseAdapter):
    module = 'bus'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST

