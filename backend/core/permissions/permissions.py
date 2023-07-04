from typing import List, Dict, Tuple
from enum import Enum
import os
import yaml
from sqlalchemy import select
from starlette.exceptions import HTTPException

from app.basic.user.models import Role
from core.service.base import BaseService
from uuid import UUID

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


def permit(*arg):
    """
    На вход дается пермит, далее логика такова
    Ищется в списке по пермиту роли, если роль сразу есть в списке пользователя, то функция дает True и заканчивается
    Если же роль не найдена, то функия идет рекурсивно по родителям ролей и так же пытается найти роль пользователя в родителях
    """

    def inner_decorator(f):
        async def wrapped(*args, **kwargs):

            service = None
            res = False
            for a in args:
                if isinstance(a, BaseService):
                    service = a
                    break
            if not service:
                raise HTTPException(status_code=403, detail=f"User not found")
            if not service.user.is_admin:
                service_roles = [UUID(i) for i in service.user.roles]
                query = select(Role).where(
                    Role.permissions_allow.contains(arg)
                ).where(
                    Role.company_id.in_(service.user.companies)
                )
                result = await service.session.execute(query)
                roles = result.scalars().all()

                if set(service_roles) & set([i.id for i in roles]):
                    res = True
                if not res:
                    parents = []
                    for r in roles:
                        if r.parents:
                            parents += r.parents
                    while parents:
                        query = select(Role).where(
                            Role.id.in_(parents)
                        ).where(
                            Role.company_id.in_(service.user.companies)
                        )
                        result = await service.session.execute(query)
                        roles = result.scalars().all()
                        if set(service_roles) & set([i.id for i in roles]):
                            res = True
                            break
                        parents = []
                        for r in roles:
                            if r.parents:
                                parents += r.parents
                if not res:
                    raise HTTPException(status_code=403,
                                        detail=f"The user ({service.user.id}) does not have permission to {arg}")
            response = f(*args, **kwargs)
            return await response

        return wrapped

    return inner_decorator
