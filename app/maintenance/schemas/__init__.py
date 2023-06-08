from .contractor import *
from .service_supplier import *


class ExceptionResponseSchema(BaseModel):
    error: str
