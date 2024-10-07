import json
from uuid import UUID

from app.prescription.prescription_config import config
from core.fastapi.adapters import BaseAdapter
from core.fastapi.adapters.action_decorator import action


class PrescriptionAdapter(BaseAdapter):
    module = 'prescription'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST
