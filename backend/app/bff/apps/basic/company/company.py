import asyncio
import uuid
from asyncio import sleep
from typing import Optional

import aiohttp
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx, htmx_init
from starlette.responses import Response
from starlette.status import HTTP_200_OK
from starlette.templating import Jinja2Templates
from app.bff.bff_config import config

from app.bff.dff_helpers.htmx_decorator import s
from app.bff.template_spec import templates

company_router = APIRouter()


class CompanyAdapter:
    headers: str
    session: aiohttp.ClientSession = None
    basic_url: str = f"http://{config.services['basic']['DOMAIN']}:{config.services['basic']['PORT']}"
    path = '/api/company'
    def __init__(self, request: Request):
        self.headers = {'Authorization': request.headers.get('Authorization') or request.cookies.get('token')}
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.close()

    async def get_company_list(self, **kwargs):

        async with self.session.get(self.basic_url + self.path) as resp:
            data = await resp.json()
        return data

    async def get_company(self, company_id: uuid.UUID):
        async with self.session.get(self.basic_url + self.path +f'/{company_id.__str__()}') as resp:
            data = await resp.json()
        return data


@company_router.get("", response_class=HTMLResponse)
@htmx(*s('basic/company/company'))
async def company(request: Request):
    return {}


@company_router.get("/table", response_class=HTMLResponse)
@htmx(*s('basic/company/company-table'))
async def company_list(request: Request):
    async with CompanyAdapter(request) as ca:
        data = await ca.get_company_list()
    return {
        'companies': data['data']
    }


@company_router.get("/card", response_class=HTMLResponse)
@htmx(*s('basic/company/company-card'))
async def company_card(request: Request, company_id: str | None = None):
    if not company_id:
        company_id = request.user.companies[0]
    async with CompanyAdapter(request) as ca:
        data = await ca.get_company(company_id)
    return {'company': data}


@company_router.get("/create-modal")
@htmx(*s('basic/company/create-modal'))
async def create_modal_company(request: Request):
    return {'hello': 'hello'}


@company_router.delete("/{company_id}")
async def delete_company(request: Request, company_id: uuid.UUID):
    return templates.TemplateResponse(
        status_code=403,
        name="/helpers/informer.html",
        context={'request': request, "title": 'Forbitten', 'message': f'You cannot delete a company record with id: {company_id} '}
    )


@company_router.put("/{company_id}")
async def edit_company(request: Request, company_id: int):
    return Response()
