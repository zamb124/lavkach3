from typing import List, Dict, Tuple
from enum import Enum
import os
import yaml
from starlette.exceptions import HTTPException

from core.service.base import BaseService
Allow = 'ALLOW'
Deny = 'Deny'


class Permissions(Enum):
    ...


def get_all_permit_fiels():
    paths = []
    path = os.path.abspath(__file__).split('/')
    ''.join(path[:-3])
    for root, dirs, files in os.walk('/'.join(path[:-3]) + '/app'):
        for file in files:
            if file.endswith(".yaml"):
                paths.append(os.path.join(root, file))
    return paths


paths = get_all_permit_fiels()
permits = {}
for path in paths:
    with open(path, "r") as stream:
        try:
            yam = yaml.safe_load(stream)
            if yam:
                for k, v in yam.get('permits').items():
                    permits.update(
                        {k: v}
                    )
        except yaml.YAMLError as exc:
            print(exc)

def permit(arg):
    def inner_decorator(f):
        def wrapped(*args, **kwargs):
            service = None
            for a in args:
                if isinstance(a, BaseService):
                    service = a
                    break
            if not service:
                raise HTTPException(status_code=403, detail=f"The user ({service.request.user.id}) does not have permission to {arg}")
            response = f(*args, **kwargs)
            print('после функции')
            return response
        print('декорируем функцию', f, 'с аргументами', arg)
        return wrapped
    return inner_decorator