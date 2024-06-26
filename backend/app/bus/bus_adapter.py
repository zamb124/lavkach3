from core.fastapi.adapters import BaseAdapter
from app.bus.bus_config import config

class BusAdapter(BaseAdapter):
    module = 'bus'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST




