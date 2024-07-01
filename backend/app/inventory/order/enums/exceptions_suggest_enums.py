from enum import Enum


class SuggestErrors(str, Enum):
    SUGGEST_ALREADY_DONE: str = 'suggest already done'
    SUGGEST_TYPE_NOT_FOUND: str = 'suggest type not found'
    SUGGEST_INVALID_VALUE: str = 'Invalid value'