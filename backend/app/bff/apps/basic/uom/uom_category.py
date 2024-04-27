from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

uom_category_router = APIRouter()


@uom_category_router.get("", response_class=HTMLResponse)
async def uom_category(request: Request):
    cls = ClassView(request, 'uom_category')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request,template, context={'cls': cls})

