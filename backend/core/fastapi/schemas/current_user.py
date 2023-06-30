from pydantic import BaseModel, UUID4
from pydantic.typing import Optional, List
from app.basic.user.services import UserService

class CurrentUser(BaseModel):
    id: Optional[UUID4]
    companies: Optional[List[UUID4]]
    roles: Optional[List[str]]
    is_admin: Optional[bool]

    class Config:
        validate_assignment = True
    async def get_user_data(self,request):
        return await UserService(request).get(self.id)
