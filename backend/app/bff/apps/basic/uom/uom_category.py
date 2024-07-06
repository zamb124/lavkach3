from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.utills import BasePermit
from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates
from fastapi import APIRouter, Depends
uom_category_router = APIRouter()


class UomCategoryPermit(BasePermit):
    permits = ['uom_category_list']


@uom_category_router.get("", response_class=HTMLResponse, dependencies=[Depends(UomCategoryPermit)])
async def uom_category(request: Request):
    cls = await ClassView(request, 'uom_category')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})
