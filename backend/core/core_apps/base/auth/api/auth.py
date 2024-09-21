from fastapi import APIRouter, Response

from .schemas import VerifyTokenRequest

auth_router = APIRouter()




@auth_router.post("/verify")
async def verify_token(request: VerifyTokenRequest):
    # await JwtService().verify_token(token=request.token)
    return Response(status_code=200)
