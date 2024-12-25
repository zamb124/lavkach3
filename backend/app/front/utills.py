import asyncio

from fastapi import Request

from app.front.template_spec import templates
from fastapi.responses import HTMLResponse

class BasePermit:
    permits: list = []

    def __init__(self, request: Request):
        ...


class BaseClass:
    permits: list = []

    def __init__(self, request: Request):
        ...


async def render(request: Request, template: str, context: dict = {}):
    if not request.scope['htmx'].hx_request:
        template = template.replace('.html', '-full.html')
    if not 'request' in context:
        context['request'] = request
    template_obj = templates.get_template(template)
    rendered_template = await template_obj.render_async(context)
    return HTMLResponse(content=rendered_template)


def convert_query_params_to_dict(query_params):
    params_dict: dict = {}
    for key, value in query_params._list:
        if old_val := params_dict.get(key):
            if isinstance(old_val, list):
                params_dict[key].append(value)
            else:
                params_dict[key] = [old_val, value]
        else:
            if key.endswith('__in'):
                params_dict[key] = [value]
            else:
                params_dict[key] = value
    return params_dict
