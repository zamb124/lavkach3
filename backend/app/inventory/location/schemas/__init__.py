from .location_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
