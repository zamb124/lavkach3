from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

store_router = APIRouter()


@store_router.get("", response_class=HTMLResponse)
async def store(request: Request):
    model = ClassView(request, 'basic', 'store')
    return templates.TemplateResponse(request,'widgets/list-full.html', context={'model': model})
