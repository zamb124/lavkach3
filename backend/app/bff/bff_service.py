from starlette.requests import Request

from app.bff.adapters import BasicAdapter


class BffService:

    @classmethod
    async def dropdown_ids(cls, request: Request, module: str, model: str, id: str, itemlink: str, is_named=False, message=None):
        """
            Виджет на вход получает модуль-модель-ид- и обратную ссылку если нужно, если нет будет /module/model/{id}
            _named означает, что так же будет отдат name для отрисовки на тайтле кнопки
        """
        async with getattr(request.scope['env'], module) as a:
            data = await a.list(model=model)
        items = []
        title = False
        for i in data.get('data'):
            if i['id'] == id:
                title = i['title']
            items.append({
                'title': i['title'],
                'url': f'{itemlink}/{i["id"]}' if itemlink else f'/{module}/{model}/{i["id"]}'
                # Если нет ссылки то отдаем ссылку на обьекты по умолчанию (form)
            })
        return {
            'model': model,
            'module': module,
            'title': title,
            'message': message,
            'items': items
        }