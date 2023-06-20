from .purchase_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
