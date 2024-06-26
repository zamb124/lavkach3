from . import bus

from .bus_adapter import BusAdapter

__domain__ = bus.__domain__
__domain__.update({
    'name': 'bus',
    'adapter': BusAdapter
})
__all__ = ['__domain__']

