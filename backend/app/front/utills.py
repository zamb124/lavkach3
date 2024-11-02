from fastapi import Request

from app.front.template_spec import templates


class BasePermit:
    permits: list = []

    def __init__(self, request: Request):
        ...


class BaseClass:
    permits: list = []

    def __init__(self, request: Request):
        ...


def render(request: Request, template: str, context: dict = {}):
    if not request.scope['htmx'].hx_request:
        template = template.replace('.html', '-full.html')
    return templates.TemplateResponse(request, template, context)
