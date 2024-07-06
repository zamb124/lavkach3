from fastapi import Request, Depends, APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.template_spec import templates
from app.bff.utills import BasePermit
from core.fastapi.frontend.constructor import ClassView

product_category_router = APIRouter()


class ProductCategoryPermit(BasePermit):
    permits = ['product_category_list']


@product_category_router.get("", response_class=HTMLResponse, dependencies=[Depends(ProductCategoryPermit)], name='Product Category')
async def product_category(request: Request):
    cls = await ClassView(request, model='product_category')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})
