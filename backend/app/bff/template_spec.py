from fastapi_htmx import htmx_init
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/bff/templates/")
