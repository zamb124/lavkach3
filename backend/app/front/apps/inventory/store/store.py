from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

store_router = APIRouter()


class StoreView(ClassView):
    """Переопределяем модель"""
    model_name = "store"

class StorePermit(BasePermit):
    permits = ['store_list']

@store_router.get("", response_class=HTMLResponse, dependencies=[Depends(StorePermit)])
async def store(request: Request):
    """Список складских ордеров"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    cls = StoreView(request)
    return templates.TemplateResponse(request, template, context={'cls': cls})



