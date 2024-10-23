from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

product_storage_type_router = APIRouter()
from fastapi import Depends

class ProductStorageTypePermit(BasePermit):
    permits = ['product_storage_type_list']


@product_storage_type_router.get("", response_class=HTMLResponse, dependencies=[Depends(ProductStorageTypePermit)])
async def product_storage_type(request: Request):
    cls = ClassView(request, model='product_storage_type')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})
