import uuid

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.template_spec import templates

user_router = APIRouter()

@user_router.post("/company_change/{company_id}", response_class=HTMLResponse)
async def company_change(request: Request, company_id: uuid.UUID):
    """
        Смена компании юзерану не па
    """

    async with request.scope['env'].basic as ba:
        data = await ba.user_company_change(user_id=request.user.user_id.hex, company_id=company_id.hex)
        message = "Company changed"
        data = await ba.dropdown_ids(request, 'basic', 'company', data['company_id'], '/basic/user/company_change', message=message)
    return templates.TemplateResponse(request, 'widgets/widgets/dropdown-ids-named-htmx.html', context=data)
