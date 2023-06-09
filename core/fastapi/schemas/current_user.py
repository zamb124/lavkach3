from pydantic import BaseModel, Field, UUID4
from pydantic.typing import Optional


class CurrentUser(BaseModel):
    id: Optional[UUID4]

    class Config:
        validate_assignment = True
