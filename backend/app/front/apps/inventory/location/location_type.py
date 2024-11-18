from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from core.frontend.constructor import ClassView

location_type_router = APIRouter()


class LocationTypeView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['location_type_list']
        super().__init__(request=request, model='location_type')


@location_type_router.get("", response_class=HTMLResponse)
async def location_type(cls: LocationTypeView = Depends()):
    """Список типов складских ордеров"""
    template = f'widgets/list{"" if cls.r.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(cls.r, template, context={'cls': cls})
