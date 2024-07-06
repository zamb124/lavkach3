import uuid
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import Response

from app.bff.bff import ExceptionResponseSchema
from app.bff.template_spec import templates
from app.bff.utills import BasePermit

user_router = APIRouter()

class UserPermit(BasePermit):
    permits = ['user_list']


@user_router.post("/company_change/{company_id}", response_class=HTMLResponse)
async def company_change(request: Request, company_id: uuid.UUID):
    """Смена компании юзерану """

    async with request.scope['env']['user'].adapter as a:
        data = await a.user_company_change(user_id=request.user.user_id.hex, company_id=company_id.hex)
        message = "Company changed"
        data = await a.dropdown_ids('company', data['company_id'], '/basic/user/company_change', message=message)
    return templates.TemplateResponse(request, 'widgets/widgets/dropdown-ids-named-htmx.html', context=data)


@user_router.get("/login", responses={"404": {"model": ExceptionResponseSchema}}, )
async def login(request: Request, response: Response):
    return templates.TemplateResponse(request, 'basic/login-full.html', context={})


@user_router.post(
    "/login",
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(
        request: Request,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()]):
    request.scope['env']
    async with request.scope['env']['user'].adapter as a:
        data = await a.login(username, password)
    return templates.TemplateResponse(request, 'components/write_ls.html',
                                      context={'token': data['token'], 'refresh_token': data['refresh_token']})


class RefreshTokenSchema(BaseModel):
    token: str
    refresh_token: str


@user_router.post("/refresh", responses={"404": {"model": ExceptionResponseSchema}}, )
async def refresh_token(request: Request, refresh_schema: RefreshTokenSchema):
    async with request.scope['env']['user'].adapter as a:
        return await a.refresh_token(refresh_schema)
