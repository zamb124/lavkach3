from pydantic import BaseModel, Field, UUID4
from pydantic.typing import Optional
from backend.app.user.services.user_service import UserService

class CurrentUser(BaseModel):
    id: Optional[UUID4]

    class Config:
        validate_assignment = True
    async def get_user_data(self):
        return await UserService().get(self.id)
