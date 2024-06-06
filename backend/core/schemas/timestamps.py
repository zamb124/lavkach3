from pydantic import BaseModel, Field
from datetime import datetime


class TimeStampScheme(BaseModel):
    created_at: datetime = Field(title='Created at', table=False)
    updated_at: datetime = Field(title='Updated at', table=False)
