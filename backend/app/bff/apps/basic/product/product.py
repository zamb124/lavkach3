from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

product_router = APIRouter()


@product_router.get("", response_class=HTMLResponse)
async def product(request: Request):
    cls = ClassView(request,  'product')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})

