from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit, render
from core.frontend.constructor import ClassView

store_router = APIRouter()


class StorePermit(BasePermit):
    permits = ['store_list']


@store_router.get("", response_class=HTMLResponse, dependencies=[Depends(StorePermit)])
async def store(request: Request):
    cls = ClassView(request, 'store')
    template = f'widgets/list.html'
    return await render(cls.r, template, context={'cls': cls})
