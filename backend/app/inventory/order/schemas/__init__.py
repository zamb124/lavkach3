from .order_schemas import *
from .order_type_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
