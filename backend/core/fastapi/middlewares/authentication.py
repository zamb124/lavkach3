from typing import Optional, Tuple
import json
import jwt
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection, HTTPException

from core.config import config
from ..schemas import CurrentUser
from ...exceptions import DecodeTokenException


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection) -> Tuple[bool, Optional[CurrentUser]]:
        current_user = CurrentUser()
        authorization: str = conn.headers.get("Authorization")
        if not authorization:
            return False, current_user
        if not authorization:
            return False, current_user
        try:
            payload = jwt.decode(
                authorization,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM],
            )
            current_user = CurrentUser(**payload)
        except jwt.exceptions.PyJWTError:
            return False, current_user
        return True, current_user
class AuthBffBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection) -> Tuple[bool, Optional[CurrentUser]]:
        current_user = CurrentUser()
        authorization: str = conn.headers.get("Authorization") or conn.cookies.get('token')
        if not authorization:
            return False, current_user
        if not authorization:
            return False, current_user
        try:
            payload = jwt.decode(
                authorization,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM],
            )
            current_user = CurrentUser(**payload)
        except jwt.exceptions.PyJWTError:
            return False, current_user
        return True, current_user


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass
