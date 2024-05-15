from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

store_router = APIRouter()


@store_router.get("", response_class=HTMLResponse)
async def store(request: Request):
    cls = ClassView(request, 'store')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template,  context={'cls': cls})
