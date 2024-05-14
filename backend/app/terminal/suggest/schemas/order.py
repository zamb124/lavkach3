from pydantic import BaseModel, UUID4
import datetime
from typing import Optional

class Order(BaseModel):
    number: str
    order_type: str
    parent_id: Optional[UUID4]
    external_number: Optional[str]
    partner_id: UUID4
    planned_date: datetime.datetime