from pydantic import BaseModel, Field
from datetime import datetime


class TimeStampScheme(BaseModel):
    created_at: datetime = Field(title='Created at', inline=False)
    updated_at: datetime = Field(title='Updated at', inline=False)
