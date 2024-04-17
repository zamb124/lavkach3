import aiohttp

from starlette.requests import Request

from app.bff.bff_config import config


#
async def interapi(method: str, service: str, request: Request, path: str):
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': request.headers.get('Authorization')}
        async with session('GET', f'{config.BASIC_APP_URL}: {config.BASIC_APP_PORT}', headers=headers) as resp:
            data = await resp.json()