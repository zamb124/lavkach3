import logging

from fastapi_restful.tasks import repeat_every
from starlette.websockets import WebSocketDisconnect

from .bus import BusFilter
from .bus.enums import BusStatus
from .bus.managers import ws_manager
from .tkq import broker
from core.env import Env
from core.helpers.cache import CacheTag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cursors = {}

@broker.task
async def send_message(message):
    env = Env.get_env()
    bs = env['bus'].service
    #filter = BusFilter(status__in=[BusStatus.NEW, BusStatus.ERROR])
    #messages = await bs.list(_filter=filter)
    active_connections = ws_manager.active_connections
    conn_to_delete = []
    for _, connection in active_connections.items():
        if connection.user.user_id.__str__() == message.get('user_id'):
            try:
                await ws_manager.send_tagged_message(
                    websocket=connection,
                    tag=CacheTag(message['cache_tag']),
                    message=message['message'],
                    vars=message['vars']
                )
            except Exception as e:
                conn_to_delete.append(_)
        elif connection.user.company_id.__str__() == message.get('company_id'):
            try:
                await ws_manager.send_tagged_message(
                    websocket=connection,
                    tag=CacheTag(message['cache_tag']),
                    message=message['message'],
                    vars=message['vars']
                )
            except Exception as e:
                conn_to_delete.append(_)
    for con in conn_to_delete:
        ws_manager.active_connections.pop(con)
    bs_entity = await bs.get(message['bus_id'])
    bs_entity.status = BusStatus.DELIVERED
    await bs.session.commit()

@broker.task
async def start_processing_messages_task():
    env = await Env.get_sudo_env()
    bs = env['bus'].service
    filter = BusFilter(status__in=[BusStatus.NEW, BusStatus.ERROR])
    messages = await bs.list(_filter=filter)
    active_connections = ws_manager.active_connections
    for _, connection in active_connections.items():
        for message in messages:
            if connection.user.company_id == message.company_id:
                try:
                    await ws_manager.send_tagged_message(
                        websocket=connection,
                        tag=message.cache_tag,
                        message=message.message,
                        vars=message.vars
                    )
                except Exception as e:
                    ws_manager.active_connections.pop(_)
                message.status = BusStatus.DELIVERED
                bs.session.add(message)
    await bs.session.commit()

@repeat_every(seconds=99999, logger=logger)
async def start_processing_messages() -> None:
    task = await start_processing_messages_task.kiq()
    res = await task.wait_result()
    return None
