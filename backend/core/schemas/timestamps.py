from pydantic import BaseModel
from datetime import datetime


class TimeStampScheme(BaseModel):
    created_at: datetime
    updated_at: datetime