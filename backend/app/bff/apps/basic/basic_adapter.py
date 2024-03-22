from app.bff.template_spec import templates
from core.fastapi.adapters import BaseAdapter
from fastapi import FastAPI, HTTPException

class BasicAdapter(BaseAdapter):
    module = 'basic'

    # async def common_exception_handler(self, responce):
    #     if responce.status_code != 200:
    #         raise HTTPException(responce.status_code, detail=f"{str(responce.text)}")
    #     return responce.json()