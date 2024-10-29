import asyncio
import logging

from fastapi_restful.tasks import repeat_every
from pydantic import BaseModel
from pydantic.v1.schema import schema

from app.front.tkq import broker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cursors = {}

@broker.task
async def import_prepare_data(model: str, data: list, ):
    env = broker.env
    model = env[model]
    import_schema: BaseModel
    header = list(data[0].keys())
    errors = []
    lines: list = []
    mode = 'create'
    if 'id' in header:
        import_schema = model.schemas.update
        mode = 'update'
    else:
        import_schema = model.schemas.create
    for i, line in enumerate(data):
        try:
            line = import_schema(**line)
        except Exception as ex:
            logger.error(f'Error in line {i}: {ex}')
            for er in ex.errors():
                errors.append({
                    'line': i+2,
                    'type': er.get('type'),
                    'msg': f"{er.get('msg')}: Input value: {er.get('input')}",
                    'field': str(er.get('loc')[0])
                })
            continue
        lines.append(line.model_dump(mode='json'))
    return errors, lines, mode

@broker.task
async def import_save(model: str, data: list):
    env = broker.env
    model = env[model]
    import_schema: BaseModel
    imported_lines: list = []
    async with model.adapter as a:
        for line in data:
            resp = await a.create(json=line, model=model.name)
            imported_lines.append(resp)
    return imported_lines