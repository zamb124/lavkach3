from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import OrderView
from app.front.utills import BasePermit, render

inventory = APIRouter()


class OrderPermit(BasePermit):
    permits = ['order_list']


class Temp:
    def __init__(self, request: Request, template=None):
        self.request = request

    async def __call__(self):
        return self.request


@inventory.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(OrderPermit)])
async def order(request: Request):
    """Список складских ордеров"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    cls = OrderView(request)
    render(request, template, context={'cls': cls})

