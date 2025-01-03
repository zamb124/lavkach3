
from . import foodhub
from .prescription_adapter import PrescriptionAdapter

__domain__ = foodhub.__domain__ # noqa
__domain__.update({
    'name': 'foodhub',
    'adapter': PrescriptionAdapter,
})
__all__ = ['__domain__']

