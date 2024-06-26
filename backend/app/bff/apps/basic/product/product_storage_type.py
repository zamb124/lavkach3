from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

product_storage_type_router = APIRouter()


@product_storage_type_router.get("", response_class=HTMLResponse)
async def product_storage_type(request: Request):
    cls = await ClassView(request, model='product_storage_type')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})

