import typing
from datetime import datetime
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader
from starlette.datastructures import URL
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from app.front.front_config import config
from core.frontend.enviroment import environment


def url_for(
        name: str,
        /,
        **path_params: typing.Any,
) -> URL:
    return '/static/' + path_params['path']  # type: ignore


template_dirs = [
    'app/front/templates',
    'app/front/apps/',
]
environment.loader.searchpath += template_dirs

templates = environment
templates.globals['datetime'] = datetime
templates.globals['uuid'] = uuid4
templates.globals['url_for'] = url_for
templates.globals['now'] = datetime.date(datetime.now()).isoformat()
templates.globals['ws'] = f"ws://{config.MESSAGE_HOST}:{config.MESSAGE_PORT}/api/bus/ws/bus"


async def internal_error(request: Request, exc: HTTPException):
    return templates.TemplateResponse('base/toast.html', {'request': request}, status_code=500)


exception_handlers = {
    500: internal_error
}
