
from . import prescription
from .prescription_adapter import PrescriptionAdapter

__domain__ = prescription.__domain__ # noqa
__domain__.update({
    'name': 'prescription',
    'adapter': PrescriptionAdapter,
})
__all__ = ['__domain__']

