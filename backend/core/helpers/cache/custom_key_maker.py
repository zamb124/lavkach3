import inspect
from typing import Callable, Any

from core.helpers.cache.base import BaseKeyMaker


class CustomKeyMaker(BaseKeyMaker):
    async def make(self, function: Any | Callable, prefix: str) -> str:
        if isinstance(function, Callable):
            path = f"{prefix}::{inspect.getmodule(function).__name__}.{function.__name__}"
            args = ""

            for arg in inspect.signature(function).parameters.values():
                args += arg.name

            if args:
                return f"{path}.{args}"
        else:
            path = f"{prefix}::{function}"

        return path
