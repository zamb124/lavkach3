from .models import Foodhub
from .schemas.prescription_schemas import PrescriptionCreateScheme, PrescriptionUpdateScheme, PrescriptionFilter, PrescriptionScheme
from .services import PrescriptionService

__domain__ = {
    'foodhub': {
        'service': PrescriptionService,
        'model': Foodhub,
        'schemas': {
            'create': PrescriptionCreateScheme,
            'update': PrescriptionUpdateScheme,
            'filter': PrescriptionFilter,
            'get': PrescriptionScheme
        }
    }
}

