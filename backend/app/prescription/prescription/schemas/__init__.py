from .prescription_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
