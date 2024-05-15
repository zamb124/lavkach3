from app.bff.bff_config import config
from app.bff.tkq import broker

from core.helpers.cache import Cache, CacheStrategy

import logging
from fastapi_restful.tasks import repeat_every
from httpx import AsyncClient as asyncclient
from core.env import Env, domains

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cursors = {}

@broker.task
async def remove_expired_tokens_celery():
    client = asyncclient()
    body = {
        "email": config.SUPERUSER_EMAIL,
        "password": config.SUPERUSER_PASSWORD
    }

    responce = await client.post(
        url=f'{config.services["basic"]["DOMAIN"]}/api/basic/user/login',
        json=body
    )
    data = responce.json()
    client = asyncclient(headers={'Authorization': data['token']})
    env = Env(domains, client)
    for domain in domains:
        for model_name, model in domain.models.items():
            if model.cache_strategy == CacheStrategy.FULL:
                while True:
                    cursor = cursors.get(model, 0)
                    async with model.adapter as a:
                        data = await a.list(params={'lsn': cursor})
                    if items := data['data']:
                        items_for_cache = {i['id']: i for i in items}
                        for k, v in items_for_cache.items():
                            await Cache.set_model(module=model.domain.name, model=model.name, key=k, data=v)
                        new_cursor = data['cursor']
                        cursors.update({model: new_cursor})
                        logger.info(f'Service: {model.domain.name} and Model: {model.name} is cached')
                        if cursor <= new_cursor:
                            break
                        logger.info(f'Service: {model.domain.name} and Model: {model.name} is cached')
                    else:
                        break

@repeat_every(seconds=350, logger=logger)
async def remove_expired_tokens() -> None:
    task = await remove_expired_tokens_celery.kiq()
    res = await task.wait_result()
    return None
