from fastapi import Request


class BasePermit:
    permits: list = []

    def __init__(self, request: Request):
        ...
