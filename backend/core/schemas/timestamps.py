from pydantic import BaseModel, Field
from datetime import datetime


class TimeStampScheme(BaseModel):
    created_at: datetime = Field(default=None, title='Created at', table=True)
    updated_at: datetime = Field(default=None, title='Updated at', table=True)
