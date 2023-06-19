from sqlalchemy import or_, select, and_
from app.user.schemas.user_schemas import LoginResponseSchema
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailOrNicknameException,
    UserNotFoundException,
)
from core.utils.token_helper import TokenHelper



from app.user.models.user_models import User
from app.user.schemas.user_schemas import UserCreateScheme, UserUpdateScheme
from core.db.session import session
from core.service.base import BaseService
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException


class UserService(BaseService[User, UserCreateScheme, UserUpdateScheme]):
    def __init__(self, db_session: session=session):
        super(UserService, self).__init__(User, db_session)

    async def create(self, obj: UserCreateScheme) -> User:
        if obj.password1 != obj.password2:
            raise PasswordDoesNotMatchException
        setattr(obj, 'password',obj.password1)
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

    async def login(self, email: str, password: str) -> LoginResponseSchema:
        result = await session.execute(
            select(User).where(and_(User.email == email, password == password))
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        response = LoginResponseSchema(
            token=TokenHelper.encode(payload={"user_id": user.id.__str__()}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
        return response

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




