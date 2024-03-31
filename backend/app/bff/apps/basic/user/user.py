import uuid

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.bff_server import config
from app.bff.bff_service import BffService
from app.bff.dff_helpers.htmx_decorator import s

user_router = APIRouter()

@user_router.post("/company_change/{company_id}", response_class=HTMLResponse)
@htmx(*s('widgets/widgets/dropdown-ids-named-htmx'))
async def company_change(request: Request, company_id: uuid.UUID):
    """
        Смена компании юзерану не па
    """

    async with request.scope['env'].basic as ba:
        data = await ba.user_company_change(user_id=request.user.user_id.hex, company_id=company_id.hex)
    message = "Company changed"
    return await BffService.dropdown_ids(request, 'basic', 'company', data['company_id'], '/basic/user/company_change', message=message)
