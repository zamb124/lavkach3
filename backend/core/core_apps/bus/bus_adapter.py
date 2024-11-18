from .bus_config import config
from ...fastapi.adapters import BaseAdapter


class BusAdapter(BaseAdapter):
    module = 'bus'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST




