from . import company
from . import store
from . import user
from . import uom
from . import partner
from . import product
from . import fundamental
from .basic_adapter import BasicAdapter

__domain__ = company.__domain__|store.__domain__| user.__domain__| uom.__domain__| partner.__domain__| product.__domain__| fundamental.__domain__
__domain__.update({
    'name': 'basic',
    'adapter': BasicAdapter
})
__all__ = ['__domain__']

