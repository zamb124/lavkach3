from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.dff_helpers.schema_recognizer import ModelView
from app.bff.template_spec import templates

product_router = APIRouter()


@product_router.get("", response_class=HTMLResponse)
async def product(request: Request):
    model = ModelView(request, 'basic', 'product')
    return templates.TemplateResponse(request,'widgets/list-full.html', context={'model': model})

