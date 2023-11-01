from typing import List, Dict, Any, Optional

from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.basic.company.services import CompanyService
from app.basic.user.models.user_models import User
from app.basic.user.models.role_models import Role
from app.basic.user.schemas.user_schemas import LoginResponseSchema, SignUpScheme
from app.basic.user.schemas.user_schemas import UserCreateScheme, UserUpdateScheme, UserFilter
from app.basic.user.services.role_service import RoleService
from core.db.session import session
from core.db.transactional import Transactional
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailOrNicknameException,
    UserNotFoundException,
)
from core.service.base import BaseService, ModelType, FilterSchemaType
from core.utils.token_helper import TokenHelper
from core.permissions.permissions import permit, permits


class UserService(BaseService[User, UserCreateScheme, UserUpdateScheme, UserFilter]):
    def __init__(self, request=None, db_session=None):
        super(UserService, self).__init__(request, User, db_session)

    @permit('user_get')
    async def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        if self.user.is_admin:
            query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    @permit('user_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(UserService, self).list(_filter, size)

    @permit('user_delete')
    async def delete(self, id: Any) -> None:
        return await super(UserService, self).delete(id)

    @permit('user_create')
    async def create(self, obj: UserCreateScheme, commit=True) -> User:
        if obj.password1 != obj.password2:
            raise PasswordDoesNotMatchException
        setattr(obj, 'password', obj.password1)
        delattr(obj, 'password1')
        delattr(obj, 'password2')
        entity = self.model(**obj.dict())
        self.session.add(entity)
        try:
            await self.session.commit()
            await self.session.refresh(entity)
        except IntegrityError as e:
            await self.session.rollback()
            if "duplicate key" in str(e):
                raise DuplicateEmailOrNicknameException
            else:
                raise e
        except Exception as e:
            raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
        return entity

    async def login(self, email: str, password: str):
        # Получаем юзера из бд
        result_user = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result_user.scalars().first()

        if not user:
            raise UserNotFoundException

        if not user.password == password:
            raise PasswordDoesNotMatchException
        # Получаем пермишены
        if not user.is_admin:
            result_roles = await self.session.execute(
                select(Role).where(Role.id.in_(user.roles))
            )
        else:
            result_roles = await self.session.execute(
                select(Role)
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
                "roles": [i.id.__str__() for i in set(roles)],
                "is_admin": user.is_admin,
                'locale': user.locale.language,
                'country': user.country.code
            }),
            'refresh_token': TokenHelper.encode(payload={"sub": "refresh"}),
            'user_id': user.id,
            'companies': companies,
            'nickname': user.nickname,
            'permissions': permissions_list,
            'store_id': user.store_id,
            'roles': [i.title for i in roles] if not user.is_admin else ['superadmin'],
            'locale': user.locale.language,
            'country': user.country.code
        }

    async def is_admin(self, user_id: int) -> bool:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False

        if user.is_admin is False:
            return False

        return user

    async def signup(self, obj: SignUpScheme):
        try:
            company = await CompanyService(db_session=self.session).sudo().create(obj.company, commit=False)
            obj.user.companies = [company.id]
            role = await RoleService(db_session=self.session).sudo().create_company_admin_role(company.id, commit=False)
            obj.user.roles = [role.id]
            user = await self.sudo().create(obj.user, commit=False)
            login = await self.login(user.email, user.password)
        except Exception as e:
            await self.session.rollback()
            if isinstance(e, DuplicateEmailOrNicknameException):
                raise e
            raise HTTPException(status_code=409, detail=f"Dublicate {str(e)}")
        await self.session.commit()
        return login

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
