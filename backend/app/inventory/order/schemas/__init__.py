from pydantic import BaseModel
from .move_schemas import (
    MoveBaseScheme,
    MoveCreateScheme,
    MoveUpdateScheme,
    MoveScheme,
    MoveFilter,
    MoveListSchema
)
from .move_log_schemas import (
    MoveLogBaseScheme,
    MoveLogCreateScheme,
    MoveLogUpdateScheme,
    MoveLogScheme,
    MoveLogFilter,
    MoveLogListSchema
)
from .order_schemas import (
    OrderBaseScheme,
    OrderCreateScheme,
    OrderUpdateScheme,
    OrderScheme,
    OrderFilter,
    OrderListSchema
)
from .order_type_schemas import (
    OrderTypeBaseScheme,
    OrderTypeCreateScheme,
    OrderTypeUpdateScheme,
    OrderTypeScheme,
    OrderTypeFilter,
    OrderTypeListSchema
)

from .suggest_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
