from ....base.auth.schemas.jwt import RefreshTokenSchema
from .....exceptions.token import DecodeTokenException
from .....utils.token_helper import TokenHelper


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
            token=TokenHelper.encode(payload={
                "user_id": token.get("user_id"),
                "company_ids": token.get('company_ids'),
                "role_ids": token.get('role_ids'),
                "is_admin": token.get('is_admin')
            }),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
