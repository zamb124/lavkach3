from backend.app.auth.schemas.jwt import RefreshTokenSchema
from backend.core.exceptions.token import DecodeTokenException
from backend.core.utils.token_helper import TokenHelper


class JwtService:
    async def verify_token(self, token: str) -> None:
        TokenHelper.decode(token=token)

    async def create_refresh_token(
        self,
        token: str,
        refresh_token: str,
    ) -> RefreshTokenSchema:
        token = TokenHelper.decode(token=token)
        refresh_token = TokenHelper.decode(token=refresh_token)
        if refresh_token.get("sub") != "refresh":
            raise DecodeTokenException

        return RefreshTokenSchema(
            token=TokenHelper.encode(payload={"user_id": token.get("user_id")}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
