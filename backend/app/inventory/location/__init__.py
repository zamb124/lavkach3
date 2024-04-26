from app.inventory.location.models import Location, LocationType
from app.inventory.location.schemas import LocationCreateScheme, LocationUpdateScheme, LocationFilter, LocationScheme, \
    LocationTypeCreateScheme, LocationTypeUpdateScheme, LocationTypeFilter, LocationTypeScheme
from app.inventory.location.services import LocationService, LocationTypeService

__domain__ = {
    'location': {
        'service': LocationService,
        'model': Location,
        'schemas': {
            'create': LocationCreateScheme,
            'update': LocationUpdateScheme,
            'filter': LocationFilter,
            'get': LocationScheme
        }
    },
    'location_type': {
        'service': LocationTypeService,
        'model': LocationType,
        'schemas': {
            'create': LocationTypeCreateScheme,
            'update': LocationTypeUpdateScheme,
            'filter': LocationTypeFilter,
            'get': LocationTypeScheme
        }
    }

}
__all__ = ['__domain__']
