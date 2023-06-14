from .contractor_schemas import *
from .service_supplier_schemas import *
from .manufacturer_schemas import *
from .model_schemas import *
from .asset_type_schemas import *
from .asset_schemas import *
from .asset_log_schemas import *
from .order_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
