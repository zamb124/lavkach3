from .user_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
