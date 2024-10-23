from fastapi import Depends, APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

product_category_router = APIRouter()


class ProductCategoryPermit(BasePermit):
    permits = ['product_category_list']


@product_category_router.get("", response_class=HTMLResponse, dependencies=[Depends(ProductCategoryPermit)], name='Product Category')
async def product_category(request: Request):
    cls = ClassView(request, model='product_category')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})
