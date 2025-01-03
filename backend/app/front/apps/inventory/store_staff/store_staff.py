from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import StoreStaffView
from app.front.template_spec import templates
from app.front.utills import render

store_staff_router = APIRouter()

@store_staff_router.get("", response_class=HTMLResponse)
async def store_staff(cls: StoreStaffView = Depends()):
    """Список перемещений"""
    template = f'widgets/list.html'
    return await render(
        cls.r,
        template,
        context={'cls': cls}
    )
