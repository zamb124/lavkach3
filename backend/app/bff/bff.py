import base64

from babel.core import LOCALE_ALIASES
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/bff/templates/")


class ExceptionResponseSchema(BaseModel):
    error: str


index_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)

@index_router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('dashboards/index.html', {'request': request})

@index_router.get('/apps/invoices/create', response_class=HTMLResponse)
async def invoice_create(request: Request):
    return templates.TemplateResponse('apps/invoices/apps-invoices-create.html', {'request': request})

@index_router.get('/apps/ecommerce/order_details', response_class=HTMLResponse)
async def invoice_create(request: Request):
    return templates.TemplateResponse('apps/ecommerce/apps-ecommerce-order_details.html', {'request': request})
