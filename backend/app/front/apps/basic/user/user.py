import uuid
from typing import Optional

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import Response

from app.front.front import ExceptionResponseSchema
from app.front.template_spec import templates
from app.front.utills import BasePermit

user_router = APIRouter()


class UserPermit(BasePermit):
    permits = ['user_list']


@user_router.post("/company_change/{company_id}", response_class=HTMLResponse)
async def company_change(request: Request, company_id: uuid.UUID):
    """Смена компании юзерану """

    async with request.scope['env']['user'].adapter as a:
        data = await a.user_company_change(user_id=request.user.user_id, company_id=company_id)
        message = "Company changed"
        data = await a.dropdown_ids('company', data['company_id'], '/basic/user/company_change', message=message)
    return templates.TemplateResponse(request, 'widgets/widgets/dropdown-ids-named-htmx.html', context=data)


@user_router.get("/login", responses={"404": {"model": ExceptionResponseSchema}}, )
async def login(request: Request, response: Response):
    try:
        referer = request.headers.get('referer').split('next=')[-1]
    except Exception:
        referer = None
    next = request.query_params.get('next') or referer
    return templates.TemplateResponse(request, 'basic/login-full.html',context={'next': next})


class LoginSchema(BaseModel):
    username: str
    password: str
    next: Optional[str] = None


@user_router.post(
    "/login",
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(request: Request, schema: LoginSchema):
    async with request.scope['env']['user'].adapter as a:
        data = await a.login(schema.username, schema.password)
    return {
            'token': data['token'],
            'refresh_token': data['refresh_token'],
            'next': schema.next,
        }

@user_router.get("/logout", responses={"404": {"model": ExceptionResponseSchema}}, )
async def logout(request: Request, response: Response):
    async with request.scope['env']['user'].adapter as a:
        data = await a.logout(request.user.user_id)

class RefreshTokenSchema(BaseModel):
    token: str
    refresh_token: str


@user_router.post("/refresh", responses={"404": {"model": ExceptionResponseSchema}}, )
async def refresh_token(request: Request, refresh_schema: RefreshTokenSchema):
    async with request.scope['env']['user'].adapter as a:
        return await a.refresh_token(refresh_schema)
