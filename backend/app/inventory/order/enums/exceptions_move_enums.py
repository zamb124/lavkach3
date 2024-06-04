from enum import Enum


class MoveErrors(str, Enum):
    WRONG_STATUS: str = 'Move is not in CREATED status'
    EQUAL_QUANT_ERROR: str = 'Source Quant and Destination Quant cannot be the same'
    DEST_QUANT_ERROR: str = "It was not possible to create and find a Stock Dest, perhaps the parameters were set incorrectly"
    SOURCE_QUANT_ERROR: str = 'It was not possible to create and find a Stock Source, perhaps the parameters were set incorrectly'