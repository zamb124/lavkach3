from fastapi_htmx import htmx_init
from starlette.templating import Jinja2Templates
from datetime import datetime

templates = Jinja2Templates(directory="app/bff/templates/")

templates.env.globals['datetime'] = datetime
a=1
