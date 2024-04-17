from fastapi import APIRouter
from app.terminal.apps.suggest.api.orders import orders_router

terminal_router = APIRouter()
terminal_router.include_router(orders_router, prefix="", tags=["frontend"])


# def load_resources():
#     templates = Jinja2Templates(directory="app/terminal/apps/suggest/templates/")
#     htmx_init(templates, file_extension='html')
#
# load_resources()


