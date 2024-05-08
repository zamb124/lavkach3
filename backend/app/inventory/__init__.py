from . import order
from . import location
from . import quant
from . import product_storage
from .inventory_adapter import InventoryAdapter

__domain__ = order.__domain__|location.__domain__| quant.__domain__
__domain__.update({
    'name': 'inventory',
    'adapter': InventoryAdapter
})
__all__ = ['__domain__']

