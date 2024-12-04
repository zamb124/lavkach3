from enum import Enum


class MoveErrors(str, Enum):
    WRONG_STATUS: str = 'Move is not in {status} status'
    EQUAL_QUANT_ERROR: str = 'Source Quant and Destination Quant cannot be the same'
    DEST_QUANT_ERROR: str = "It was not possible to create and find a Stock Dest, perhaps the parameters were set incorrectly"
    SOURCE_LOCATION_ERROR: str = 'It was not possible to create and find a Source Location, perhaps some the parameters in Configuration were set incorrectly'
    DESTINATION_LOCATION_ERROR: str = 'It was not possible to create and find a Destination Location, perhaps some the parameters in Configuration were set incorrectly'
    SOURCE_QUANT_ERROR: str = 'It was not possible to create and find a Stock Source, perhaps the parameters were set incorrectly'
    RESERVATION_FAILED: str = 'Reservation failed for move {move_id}'
    SUGGESTS_ALREADY_CREATED: str = 'Suggests already created for move {move_id}'
    RESERVATION_ALREADY_CREATED: str = 'Reservation already created for move {move_id}'
    SET_DONE_ERROR: str = 'Move SET_DONE_ERROR'
    SUGGESTS_NOT_DONE: str = 'Suggests not done for move {move_id}'
    CHANGE_LOCATION_ERROR: str = 'Change location error for move {move_id}'
    PRODUCT_STORAGE_TYPE_ERROR: str = 'The product {product} does not have a storage strategy'
    MOVE_ID_ERROR: str = 'Move ID error'
    PACKAGE_ERROR: str = 'Package error'

class OrderErrors(str, Enum):
    WRONG_STATUS: str = 'Move is not in CREATED status'
    EQUAL_QUANT_ERROR: str = 'Source Quant and Destination Quant cannot be the same'
    DEST_QUANT_ERROR: str = "It was not possible to create and find a Stock Dest, perhaps the parameters were set incorrectly"
    SOURCE_QUANT_ERROR: str = 'It was not possible to create and find a Stock Source, perhaps the parameters were set incorrectly'
    RESERVATION_FAILED: str = 'Reservation failed for move {move_id}'
    SUGGESTS_ALREADY_CREATED: str = 'Suggests already created for move {move_id}'
    RESERVATION_ALREADY_CREATED: str = 'Reservation already created for move {move_id}'
