from .quants_schemas import *
from .lot_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
