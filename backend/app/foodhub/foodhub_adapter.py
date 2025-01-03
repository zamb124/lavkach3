from app.foodhub.prescription_config import config
from core.fastapi.adapters import BaseAdapter


class PrescriptionAdapter(BaseAdapter):
    module = 'foodhub'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST
