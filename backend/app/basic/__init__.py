from . import partner
from . import product
from . import store
from . import uom
from .basic_adapter import BasicAdapter

__domain__ = store.__domain__ | uom.__domain__ | partner.__domain__| product.__domain__
__domain__.update({
    'name': 'basic',
    'adapter': BasicAdapter,
})
__all__ = ['__domain__']

