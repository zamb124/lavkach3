from datetime import datetime
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.bff.bff_config import config

a=1

template_path = "app/bff/templates/"

templates = Jinja2Templates(directory=template_path)
environment = templates.env
templates.env.globals['datetime'] = datetime
templates.env.globals['uuid'] = uuid4
templates.env.globals['now'] = datetime.date(datetime.now()).isoformat()
templates.env.globals['ws'] = f"ws://{config.MESSAGE_HOST}:{config.MESSAGE_PORT}/api/bus/ws/bus"


async def internal_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse('base/toast.html', {'request': request}, status_code=500)


exception_handlers = {
    500: internal_error
}
