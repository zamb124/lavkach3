from starlette.exceptions import HTTPException
from starlette.requests import Request


class CompanyMidlleWare:
    def __init__(self, name: str, *args, **kwargs):
        self.name = name

    def __call__(self, request: Request):
        if "companies" not in request.cookies:
            raise HTTPException(status_code=403, detail="Запрещено")
        # проверяем что в куках есть инфа о наличии прав пользователя
        return True


company_depends = CompanyMidlleWare("Companies")