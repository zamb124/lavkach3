from typing import Any, List
from uuid import UUID

from sqlalchemy import select, Row, RowMapping
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.basic.user.models.role_models import Role
from app.basic.user.models.user_models import User
from app.basic.user.schemas.user_schemas import SignUpScheme, ChangeCompanyScheme
from app.basic.user.schemas.user_schemas import UserCreateScheme, UserUpdateScheme, UserFilter
# from app.basic.user.services.role_service import RoleService
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailOrNicknameException,
    UserNotFoundException,
)
# from core.fastapi.schemas import CurrentUser
from core.permissions.permissions import permit, permits
from core.service.base import BaseService, ModelType, FilterSchemaType
from core.utils.token_helper import TokenHelper


class UserService(BaseService[User, UserCreateScheme, UserUpdateScheme, UserFilter]):
    def __init__(self, request: Request):
        super(UserService, self).__init__(request, User, UserCreateScheme, UserUpdateScheme)

    @permit('user_get')
    async def get(self, id: Any) -> Row | RowMapping:
        return await super(UserService, self).get(id)

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

    async def login(self, email: str = None, password: str = None, user = None):
        # Получаем юзера из бд
        if not user:
            result_user = await self.session.execute(
                select(User).where(User.email == email)
            )
            user = result_user.scalars().first()

            if not user:
                raise UserNotFoundException

            if not user.password == password:
                raise PasswordDoesNotMatchException
        else:
            result_user = await self.session.execute(
                select(User).where(User.id == user.user_id)
            )
            user = result_user.scalars().first()
        # Получаем пермишены
        if not user.is_admin:
            result_roles = await self.session.execute(
                select(Role).where(Role.id.in_(user.role_ids))
            )
        else:
            result_roles = await self.session.execute(
                select(Role)
            )
        roles = result_roles.scalars().all()
        permissions_list = []
        for role in roles:
            permissions_list += role.permission_allow_list
        permissions_cleaned = set(permissions_list)
        permissions_list = []
        for perm in permits:
            if perm in permissions_cleaned:
                permissions_list.append(perm)
        company_ids = [i.__str__() for i in user.company_ids] if user.company_ids else []
        return {
            'token': TokenHelper.encode(payload={
                "user_id": user.id.__str__(),
                "company_ids": company_ids,
                "company_id": user.company_id.__str__() if user.company_id else None,
                "role_ids": [i.id.__str__() for i in set(roles)],
                'store_id': user.store_id.hex if user.store_id else None,
                "is_admin": user.is_admin,
                'locale': user.locale.language,
                'country': user.country.code,
                'email': user.email,
                'nickname': user.nickname,
            }),
            'refresh_token': TokenHelper.encode(payload={"sub": "refresh"}),
            'user_id': user.id,
            'email': user.email,
            'company_ids': company_ids,
            "company_id": user.company_id if user.company_id else None,
            'nickname': user.nickname,
            'permission_list': permissions_list,
            'store_id': user.store_id.hex if user.store_id else None,
            'role_ids': [i.title for i in roles] if not user.is_admin else ['superadmin'],
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
            obj.user.company_ids = [company.id]
            role = await RoleService(db_session=self.session).sudo().create_company_admin_role(company.id, commit=False)
            obj.user.role_ids = [role.id]
            user = await self.sudo().create(obj.user, commit=False)
            login = await self.login(user.email, user.password)
        except Exception as e:
            await self.session.rollback()
            if isinstance(e, DuplicateEmailOrNicknameException):
                raise e
            raise HTTPException(status_code=409, detail=f"Dublicate {str(e)}")
        await self.session.commit()
        return login

    @permit('company_change')
    async def company_change(self, obj: ChangeCompanyScheme, commit=True) -> ModelType:
        user = await self.get(obj.user_id)
        user.company_id = obj.company_id
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def permissions(self, user_id: UUID) -> List[str]:
        permits_allow: list[str] = []
        permits_deny: list[str]  =  []
        user_entity = await self.get(user_id)
        role_service = self.env['role'].service
        roles = await role_service.list(_filter={'id__in': user_entity.role_ids})
        children = []
        for r in roles:
            permits_allow += r.permission_allow_list
            permits_deny  += r.permission_deny_list
            children += r.role_ids
        while children:
            child_roles_entities = await role_service.list(_filter={'id__in': children})
            children = []
            for child in child_roles_entities:
                permits_allow += child.permission_allow_list
                permits_deny += child.permission_deny_list
                children += child.role_ids
        return list(set(permits_allow) - set(permits_deny))
