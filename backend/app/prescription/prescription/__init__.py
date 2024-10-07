from core.helpers.cache import CacheStrategy
from .models import Prescription
from .schemas.prescription_schemas import PrescriptionCreateScheme, PrescriptionUpdateScheme, PrescriptionFilter, PrescriptionScheme
from .services import PrescriptionService

__domain__ = {
    'prescription': {
        'service': PrescriptionService,
        'model': Prescription,
        'schemas': {
            'create': PrescriptionCreateScheme,
            'update': PrescriptionUpdateScheme,
            'filter': PrescriptionFilter,
            'get': PrescriptionScheme
        }
    }
}

