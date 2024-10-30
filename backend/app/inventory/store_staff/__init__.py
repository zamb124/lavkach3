from app.inventory.store_staff.models import StoreStaff
from app.inventory.store_staff.schemas import (StoreStaffCreateScheme, StoreStaffUpdateScheme,
                                               StoreStaffFilter, StoreStaffScheme)
from app.inventory.store_staff.services import StoreStaffService

__domain__ = {
    'store_staff': {
        'service': StoreStaffService,
        'model': StoreStaff,
        'schemas': {
            'create': StoreStaffCreateScheme,
            'update': StoreStaffUpdateScheme,
            'filter': StoreStaffFilter,
            'get': StoreStaffScheme
        }
    }
}
__all__ = ['__domain__']
