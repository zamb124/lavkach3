from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

product_router = APIRouter()


@product_router.get("", response_class=HTMLResponse)
async def product(request: Request):
    cls = ClassView(request,  'product')
    return templates.TemplateResponse(request,'widgets/list-full.html', context={'cls': cls})

