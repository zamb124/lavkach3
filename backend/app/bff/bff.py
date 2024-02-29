import base64

from babel.core import LOCALE_ALIASES
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response, Request

from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx_init, htmx, TemplateSpec as ts
from app.bff.template_spec import templates
from app.bff.dff_helpers.htmx_decorator import s

htmx_init(templates, file_extension='html')


class ExceptionResponseSchema(BaseModel):
    error: str





index_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)

@index_router.get("/", response_class=HTMLResponse)
@htmx(*s('index'))
async def root_page(request: Request):
    return {"greeting": "Hello World"}


@index_router.get("/", response_class=HTMLResponse)
@htmx(*s('index'))
async def root_page(request: Request):
    return {"greeting": "Hello World"}
