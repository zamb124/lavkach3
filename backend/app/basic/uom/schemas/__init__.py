from .uom_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
