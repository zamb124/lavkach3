from enum import Enum


class TextColorEnum(str, Enum):
    PRIMARY:        str = 'primary'
    SECONDARY:      str = 'secondary'
    SUCCESS:        str = 'success'
    INFO:           str = 'info'
    WARNING:        str = 'warning'
    DANGER:         str = 'danger'
    DARK:           str = 'dark'
    LIGHT:          str = 'light'
