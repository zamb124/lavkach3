
#
# @orders_router.get("/suggests", response_class=HTMLResponse)
# # @htmx(*s('order-kanban'))
# async def suggest(request: Request):
#     pass
# @orders_router.websocket("/suggest_ws")
# async def suggest_handler(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         msg = await websocket.receive_json()
#         await websocket.send_text(
#             content.format(time=time.time(), message=msg["chat_message"])
#         )
#         # каждый результат отправляем бэкенду