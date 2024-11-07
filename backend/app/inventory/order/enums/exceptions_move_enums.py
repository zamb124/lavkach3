from enum import Enum


class MoveErrors(str, Enum):
    WRONG_STATUS: str = 'Move is not in CREATED status'
    EQUAL_QUANT_ERROR: str = 'Source Quant and Destination Quant cannot be the same'
    DEST_QUANT_ERROR: str = "It was not possible to create and find a Stock Dest, perhaps the parameters were set incorrectly"
    SOURCE_QUANT_ERROR: str = 'It was not possible to create and find a Stock Source, perhaps the parameters were set incorrectly'
    RESERVATION_FAILED: str = 'Reservation failed for move {move_id}'
    SUGGESTS_ALREADY_CREATED: str = 'Suggests already created for move {move_id}'
    RESERVATION_ALREADY_CREATED: str = 'Reservation already created for move {move_id}'
    SET_DONE_ERROR: str = 'Move SET_DONE_ERROR'

class OrderErrors(str, Enum):
    WRONG_STATUS: str = 'Move is not in CREATED status'
    EQUAL_QUANT_ERROR: str = 'Source Quant and Destination Quant cannot be the same'
    DEST_QUANT_ERROR: str = "It was not possible to create and find a Stock Dest, perhaps the parameters were set incorrectly"
    SOURCE_QUANT_ERROR: str = 'It was not possible to create and find a Stock Source, perhaps the parameters were set incorrectly'
    RESERVATION_FAILED: str = 'Reservation failed for move {move_id}'
    SUGGESTS_ALREADY_CREATED: str = 'Suggests already created for move {move_id}'
    RESERVATION_ALREADY_CREATED: str = 'Reservation already created for move {move_id}'