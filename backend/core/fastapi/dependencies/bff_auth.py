from abc import ABC, abstractmethod
from typing import List, Type

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase

from app.basic.user.services.user_service import UserService
from core.exceptions import CustomException, UnauthorizedException



class Token:
    async def token(self, request: Request) -> str | None:
        return request.headers.get('Authorization')

