from app.prescription.prescription_config import config
from core.fastapi.adapters import BaseAdapter


class PrescriptionAdapter(BaseAdapter):
    module = 'prescription'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST
