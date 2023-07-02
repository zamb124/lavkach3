from typing import List, Dict, Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

from app.basic.user.models.user_models import User
from app.basic.user.models.role_models import Role
from app.basic.user.schemas.user_schemas import LoginResponseSchema
from app.basic.user.schemas.user_schemas import UserCreateScheme, UserUpdateScheme, UserFilter
from core.db.session import session
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailOrNicknameException,
    UserNotFoundException,
)
from core.service.base import BaseService, ModelType
from core.utils.token_helper import TokenHelper
from core.permissions.permissions import permit, permits


class UserService(BaseService[User, UserCreateScheme, UserUpdateScheme, UserFilter]):
    def __init__(self, request, db_session: session = session):
        super(UserService, self).__init__(request, User, db_session)

    async def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        if self.request.user.is_admin:
            query = select(self.model).where(self.model.id == id)
        result = await session.execute(query)
        return result.scalars().first()

    # @permit('user_create')
    async def create(self, obj: UserCreateScheme) -> User:
        if obj.password1 != obj.password2:
            raise PasswordDoesNotMatchException
        setattr(obj, 'password', obj.password1)
        delattr(obj, 'password1')
        delattr(obj, 'password2')
        entity = self.model(**obj.dict())
        session.add(entity)
        try:
            await session.commit()
            await session.refresh(entity)
        except IntegrityError as e:
            await session.rollback()
            if "duplicate key" in str(e):
                raise DuplicateEmailOrNicknameException
            else:
                raise e
        except Exception as e:
            raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
        return entity

    async def login(self, email: str, password: str):
        # Получаем юзера из бд
        result_user = await session.execute(
            select(User).where(and_(User.email == email, password == password))
        )
        user = result_user.scalars().first()
        if not user:
            raise UserNotFoundException
        # Получаем пермишены
        result_roles = await session.execute(
            select(Role).where(Role.id.in_(user.roles))
        )
        roles = result_roles.scalars().all()
        permissions_list = []
        for role in roles:
            permissions_list += role.permissions_allow
        permissions_cleaned = set(permissions_list)
        permissions_list = []
        for perm in permits:
            if perm in permissions_cleaned:
                permissions_list.append(perm)
        companies = [i.__str__() for i in user.companies] if user.companies else []
        return {
            'token': TokenHelper.encode(payload={
                "user_id": user.id.__str__(),
                "companies": companies,
                "roles": [i.id.__str__() for i in roles],
                "is_admin": user.is_admin
            }),
            'refresh_token': TokenHelper.encode(payload={"sub": "refresh"}),
            'companies': companies,
            'nickname': user.nickname,
            'permissions': permissions_list,
            'store_id': user.store_id,
            'roles': [i.title for i in roles],
            'locale': user.locale
        }

    async def is_admin(self, user_id: int) -> bool:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False

        if user.is_admin is False:
            return False

        return user

# class UserService:
#
#     @Transactional(propagation=Propagation.REQUIRED)
#     async def create_user(
#         self, email: str, password1: str, password2: str, nickname: str, type:str, store_id: uuid.UUID
#     ) -> None:
#         if password1 != password2:
#             raise PasswordDoesNotMatchException
#
#         query = select(User).where(or_(User.email == email, User.nickname == nickname))
#         result = await session.execute(query)
#         is_exist = result.scalars().first()
#         if is_exist:
#             raise DuplicateEmailOrNicknameException
#
#         user = User(email=email, password=password1, nickname=nickname)
#         session.add(user)
