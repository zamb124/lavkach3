from .contractor import *
from .service_supplier import *
from .manufacturer import *


class ExceptionResponseSchema(BaseModel):
    error: str
