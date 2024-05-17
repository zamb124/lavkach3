from enum import Enum

from pydantic import BaseModel

from core.schemas import BaseFilter


class Format(str, Enum):
    jpg = 'jpg'

class Image(BaseModel):
    file_data: str
    filename: str
    format: Format


