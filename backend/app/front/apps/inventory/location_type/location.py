from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

location_router = APIRouter()


class LocationView(ClassView):
    """Переопределяем модель"""

    def __init__(self, request: Request):
        permits = ['location_list']
        super().__init__(request=request, model='location')


@location_router.get("", response_class=HTMLResponse)
async def location(cls: LocationView = Depends()):
    """Список типов складских ордеров"""
    template = f'widgets/list{"" if cls.r.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(cls.r, template, context={'cls': cls})
