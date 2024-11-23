from enum import Enum


class OrderTypeErrors(str, Enum):
    SOURCE_LOCATION_ERROR: str = "No allowed zones found for the package"