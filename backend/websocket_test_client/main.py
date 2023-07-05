import argparse

from websockets import connect

import asyncio



async def listen(token: str):
    async with connect(
        f"ws://localhost:8080/ws/bus?token={token}"
    ) as websocket:
        await websocket.send("Hello world!")
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")


if __name__ == '__main__':
    asyncio.run(listen('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZTY0MGY2ZjEtNDIyMC00NDE4LTkyN2MtNmI3MmYwMWMyMGYzIiwiY29tcGFuaWVzIjpbImY4OGFiMzA1LTI3ZDUtNGJlYy05ZmQ2LTk2ODFmOTBiNzM1YSJdLCJyb2xlcyI6WyJmNDJmOGRkYi0wN2YxLTQzMzctOTI4Ni1jNzQ4MTkyNTk1NDIiXSwiaXNfYWRtaW4iOmZhbHNlLCJleHAiOjE2ODg1MDM1MTZ9.uCt-RFQLzfhTzI2nNADmXH7QtsKbEk0fah-LwQMiaAY'))
