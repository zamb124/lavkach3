import asyncio
import uuid
from asyncio import sleep

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx, htmx_init
from starlette.responses import Response
from starlette.status import HTTP_200_OK
from starlette.templating import Jinja2Templates

from app.bff.dff_helpers.htmx_decorator import s

company_router = APIRouter()


@company_router.get("", response_class=HTMLResponse)
@htmx(*s('basic/company/company'))
async def company(request: Request):
    return {
        "companies": [
            {
                'id': '1',
                'title': 'title',
                'external_id': 'external_id',
                'country': 'country',
                'locale': 'locale',
                'currency': 'currency',
            },
            {
                'id': '2',
                'title': 'title2',
                'external_id': 'external_id',
                'country': 'country',
                'locale': 'locale',
                'currency': 'currency',
            },
        ]
    }


@company_router.get("/table", response_class=HTMLResponse)
@htmx(*s('basic/company/company-table'))
async def company_list(request: Request):
    await asyncio.sleep(2)
    return {
        "companies": [
            {
                'id': '1',
                'title': 'title',
                'external_id': 'external_id',
                'country': 'country',
                'locale': 'locale',
                'currency': 'currency',
            },
            {
                'id': '2',
                'title': 'title2',
                'external_id': 'external_id',
                'country': 'country',
                'locale': 'locale',
                'currency': 'currency',
            },
        ]
    }


@company_router.get("/short-card", response_class=HTMLResponse)
@htmx(*s('basic/company/company-short-card'))
async def company_list(request: Request):
    await asyncio.sleep(3)
    return {
        "company":
            {
                'id': '1',
                'title': 'Suka Solutions',
                'external_id': 'external_id',
                'country': 'Russia',
                'locale': 'locale',
                'currency': 'currency',
            }
    }

@company_router.get("/short-card", response_class=HTMLResponse)
@htmx(*s('basic/company/company-card'))
async def company_create(request: Request):
    await asyncio.sleep(5)
    return {
        "company":
            {
                'id': '1',
                'title': 'Suka Solutions',
                'external_id': 'external_id',
                'country': 'Russia',
                'locale': 'locale',
                'currency': 'currency',
            }
    }


@company_router.get("/create-modal")
@htmx(*s('basic/company/create-modal'))
async def create_modal_company(request: Request):
    return {'hello': 'hello'}

@company_router.delete("/{company_id}")
@htmx(*s('helpers/sw-dialog'))
async def delete_company(request: Request, company_id: int):
    return {'company_id': company_id}


@company_router.put("/{company_id}")
async def edit_company(request: Request, company_id: int):
    return Response()
