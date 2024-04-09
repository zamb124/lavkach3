from app.bff.bff_config import config

from core.helpers.cache import Cache

cursors = {}
import logging
from fastapi_restful.tasks import repeat_every
from httpx import AsyncClient as asyncclient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@repeat_every(seconds=360, logger=logger)
async def remove_expired_tokens() -> None:
    client = asyncclient()
    body = {
        "email": config.SUPERUSER_EMAIL,
        "password": config.SUPERUSER_PASSWORD
    }
    responce = await client.post(
        url=f'http://{config.services["basic"]["DOMAIN"]}:{config.services["basic"]["PORT"]}/api/basic/user/login',
        json=body
    )
    data = responce.json()
    client = asyncclient(headers={'Authorization': data['token']})
    for service, values in config.services.items():
        for model in values.get('schema').keys():
            adapter = values['adapter']
            while True:
                cursor = cursors.get(model, 0)
                async with adapter(conn=client, conf=values, model=model) as a:
                    data = await a.list(params={'lsn': cursor})
                if items := data['data']:
                    items_for_cache = {i['id']: i for i in items}
                    for k, v in items_for_cache.items():
                        await Cache.set_model(module=service, model=model, key=k, data=v)
                        await Cache.get_model(module=service, model=model, key=k)
                    new_cursor = data['cursor']
                    cursors.update({model: new_cursor})
                    logger.info(f'Service: {service} and Model: {model} is cached')
                    if cursor <= new_cursor:
                        break
                    logger.info(f'Service: {service} and Model: {model} is cached')
                else:
                    break
