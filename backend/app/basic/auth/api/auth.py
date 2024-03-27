from fastapi import APIRouter, Response

from .schemas import RefreshTokenRequest, VerifyTokenRequest, RefreshTokenResponse
from app.basic.auth.services.jwt import JwtService
from app.basic.user.schemas import ExceptionResponseSchema

auth_router = APIRouter()




@auth_router.post("/verify")
async def verify_token(request: VerifyTokenRequest):
    await JwtService().verify_token(token=request.token)
    return Response(status_code=200)
