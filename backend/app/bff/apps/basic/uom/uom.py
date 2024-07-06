from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.template_spec import templates
from app.bff.utills import BasePermit
from core.fastapi.frontend.schema_recognizer import ClassView

uom_router = APIRouter()
from fastapi import Depends
class UomPermit(BasePermit):
    permits = ['uom_list']


@uom_router.get("", response_class=HTMLResponse, dependencies=[Depends(UomPermit)])
async def uom(request: Request):
    cls = await ClassView(request, 'uom')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})

