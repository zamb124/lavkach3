from fastapi_htmx import htmx_init
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from datetime import datetime

templates = Jinja2Templates(directory="app/bff/templates/")

templates.env.globals['datetime'] = datetime
templates.env.globals['now'] = datetime.date(datetime.now()).isoformat()
a=1

async def internal_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse('base/toast.html', {'request': request}, status_code=500)


exception_handlers = {
    500: internal_error
}
