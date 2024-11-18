from fastapi import Request


class Token:
    async def token(self, request: Request) -> str | None:
        return request.headers.get('Authorization')

