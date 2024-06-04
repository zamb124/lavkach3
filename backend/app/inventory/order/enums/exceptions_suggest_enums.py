from enum import Enum


class SuggestErrors(str, Enum):
    SUGGEST_ALREADY_DONE: str = 'suggest already done'