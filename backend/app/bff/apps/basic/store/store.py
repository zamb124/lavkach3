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

from app.bff.adapters import BasicAdapter

@company_router.get("", response_class=HTMLResponse)
@htmx(*s('basic/select/store'))
async def company(request: Request):
    async with BasicAdapter(request) as ca:
        data = await ca.get_company_list()
    return {
        'companies': data['data']
    }


