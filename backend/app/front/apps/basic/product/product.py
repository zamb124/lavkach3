from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

product_router = APIRouter()

class ProductPermit(BasePermit):
    permits = ['product_list']

@product_router.get("", response_class=HTMLResponse, dependencies=[Depends(ProductPermit)])
async def product(request: Request):
    cls = ClassView(request,  model='product')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})

