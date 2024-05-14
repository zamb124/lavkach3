import asyncio
import logging
import random

from app.bff.dff_helpers.schema_recognizer import ModelView
from app.bff.template_spec import templates
from app.terminal.suggest.schemas.order import Order
from sse_starlette.sse import EventSourceResponse
from starlette.responses import HTMLResponse

from fastapi import APIRouter, WebSocket, Request

orders_router = APIRouter()
_logger = logging.getLogger(__name__)

#
# #/terminal/main
@orders_router.get("/main", response_class=HTMLResponse)
async def company(request: Request):
    return {}


 # используем вебсокеты для ожидания ордеров от бэкенда
@orders_router.websocket("/orders_ws")
async def orders_websocket(websocket: WebSocket):
    await websocket.accept()

    # while True:

    orders_data = [
        {
            "number": "PO-001",
            "order_type": "acceptance",
            "parent_id": None,
            "external_number": "EXT-001",
            "partner_id": "5b0f6c8b-04c5-4a9c-ae8d-3d0b8e1b9ec6",
            "planned_date": "2023-01-01T00:00:00"
        },
        {
            "number": "PO-002",
            "order_type": "acceptance",
            "parent_id": None,
            "external_number": None,
            "partner_id": "5b0f6c8b-04c5-4a9c-ae8d-3d0b8e1b9ec8",  # нужно доставать по умолчанию name объекта, схема запроса != схеме в бд!
            "planned_date": "2023-01-02T00:00:00"
        }
    ]

    orders_from_inventory = [Order(**order) for order in orders_data]

    template_response = templates.TemplateResponse(name='order-msg-socket.html',
                                                   context={'request': websocket, 'orders': orders_from_inventory})

    # _logger.info(template_response.render(template_response.body))
    while True:
        await websocket.send_text(
            template_response.body.decode()
        )
        # await websocket.send_text('test')
        await asyncio.sleep(10)


@orders_router.get("/orders")
# @htmx(*s('order-msg-socket'))
async def orders_handler(request: Request):

    mock_orders_data = [
        {
            "number": "PO-001",
            "order_type": "acceptance",
            "parent_id": None,
            "external_number": "EXT-001",
            "partner_id": "5b0f6c8b-04c5-4a9c-ae8d-3d0b8e1b9ec6",
            "planned_date": "2023-01-01T00:00:00"
        },
        {
            "number": "PO-002",
            "order_type": "acceptance",
            "parent_id": None,
            "external_number": None,
            "partner_id": "5b0f6c8b-04c5-4a9c-ae8d-3d0b8e1b9ec8",  # нужно доставать по умолчанию name объекта, схема запроса != схеме в бд!
            "planned_date": "2023-01-02T00:00:00"
        }
    ]

    orders_from_inventory = [Order(**order) for order in mock_orders_data]

    model = ModelView(request, 'inventory', 'order')
    return templates.TemplateResponse(request, 'widgets/list-full.html', context={'model': model})



STREAM_DELAY = 10  # second
RETRY_TIMEOUT = 15000  # milisecond

@orders_router.get('/events')
async def message_stream(request: Request):
    def new_messages():
        yield 'orders_updated'
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            if new_messages():
                _logger.info('event %s', "orders_updated")
                yield {
                        "event": "orders_updated",
                        "id": "message_id" + str(random.randint(1, 1000000)),
                        "retry": RETRY_TIMEOUT,
                        "data": "message_content"
                }

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())



@orders_router.get("/view_orders", response_class=HTMLResponse)
async def company(request: Request):
    model = ModelView(request, 'terminal', 'order')
    return templates.TemplateResponse(request, 'widgets/list-full.html', context={'model': model})
