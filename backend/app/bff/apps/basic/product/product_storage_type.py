from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.dff_helpers.schema_recognizer import ModelView
from app.bff.template_spec import templates

product_storage_type_router = APIRouter()


@product_storage_type_router.get("", response_class=HTMLResponse)
async def product_storage_type(request: Request):
    model = ModelView(request, 'basic', 'product_storage_type')
    return templates.TemplateResponse(request,'widgets/list-full.html', context={'model': model})

