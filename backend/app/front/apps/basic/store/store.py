from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

store_router = APIRouter()


class StorePermit(BasePermit):
    permits = ['store_list']


@store_router.get("", response_class=HTMLResponse, dependencies=[Depends(StorePermit)])
async def store(request: Request):
    cls = ClassView(request, 'store')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})
