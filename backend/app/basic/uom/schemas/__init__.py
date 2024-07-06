from .uom_category_schemas import *
from .uom_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
