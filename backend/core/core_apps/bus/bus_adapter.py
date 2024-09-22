from ...fastapi.adapters import BaseAdapter
from .bus_config import config

class BusAdapter(BaseAdapter):
    module = 'bus'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST




