from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.template_spec import templates
from app.bff.utills import BasePermit
from core.frontend.constructor import ClassView

company_router = APIRouter()


class CompanyPermit(BasePermit):
    permits = ['company_list']


@company_router.get("", response_class=HTMLResponse, dependencies=[Depends(CompanyPermit)])
async def company(request: Request):
    cls = ClassView(request, model='company')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})
