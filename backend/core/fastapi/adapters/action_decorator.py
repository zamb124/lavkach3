from functools import wraps
from typing import Iterable

from pydantic import BaseModel

actions = {

}


def action(model:str, schema:BaseModel=None, multiple: bool = False, permits: Iterable = ()):
    """
        Декоратор регистрирует функцию
    """
    def decorate(func, *args, **kwargs):
        func_dict = {
                        'name': func.__name__,
                        'tkey': f't-{func.__name__}',
                        'function': func,
                        'permits': permits,
                        'doc': func.__doc__,
                        'tkey_doc': f't-{func.__name__}_doc',
                        'schema': schema,
                        'multiple': multiple
                    }
        if model_action := actions.get(model):
            model_action.update({
                func.__name__: func_dict
            })
        else:
            actions.update({
                model: {
                    func.__name__: func_dict
                }
            })

        @wraps(func)
        async def wrapped(*args, **kwargs):
            response = await func(*args, **kwargs)
            return response

        return wrapped

    return decorate
