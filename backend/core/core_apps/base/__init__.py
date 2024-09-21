from . import company
from . import fundamental
from . import user
from .base_adapter import BaseAdapter

__domain__ = company.__domain__| user.__domain__| fundamental.__domain__
__domain__.update({
    'name': 'base',
    'adapter': BaseAdapter,
})
__all__ = ['__domain__']

