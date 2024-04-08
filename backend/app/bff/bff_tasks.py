from fastapi_restful.tasks import repeat_every

from app.bff.bff_config import config
from app.bff.bff_server import app, logger


@app.on_event("startup")
@repeat_every(seconds=60, logger=logger, raise_exceptions=True, max_repetitions=None)
async def redis_cache_sync():
    print('tick')
    services = config.services.items()
    for service, vals in config.services.items():
        a=1

