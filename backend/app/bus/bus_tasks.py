from app.bus.bus import BusFilter
from app.bus.bus.enums import BusStatus
from app.bus.bus.managers import ws_manager
from core.db_config import config
from app.bus.bus_config import config as bus_config
from app.bus.tkq import broker

from core.helpers.cache import Cache, CacheStrategy, CacheTag

import logging
from fastapi_restful.tasks import repeat_every
from httpx import AsyncClient as asyncclient, request
from core.env import Env
from app.bus.bus.services.bus_service import BusService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cursors = {}

@broker.task
async def start_processing_messages_task():
    env = await Env.get_sudo_env()
    bs = env['bus'].service
    to_done = []
    filter = BusFilter(status__in=[BusStatus.NEW, BusStatus.ERROR])
    messages = await bs.list(_filter=filter)
    active_connections = ws_manager.active_connections
    for _, connection in active_connections.items():
        for message in messages:
            if connection.user.company_id == message.company_id:
                await ws_manager.send_tagged_message(websocket=connection, tag=message.cache_tag, message=message.message)
                message.status = BusStatus.DELIVERED
                bs.session.add(message)
    await bs.session.commit()

@repeat_every(seconds=20, logger=logger)
async def start_processing_messages() -> None:
    task = await start_processing_messages_task.kiq()
    res = await task.wait_result()
    return None
