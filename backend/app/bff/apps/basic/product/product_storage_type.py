from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

product_storage_type_router = APIRouter()


@product_storage_type_router.get("", response_class=HTMLResponse)
async def product_storage_type(request: Request):
    model = ClassView(request, 'basic', 'product_storage_type')
    return templates.TemplateResponse(request,'widgets/list-full.html', context={'model': model})

