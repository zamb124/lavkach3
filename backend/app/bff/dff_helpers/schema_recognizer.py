import datetime
import typing

from pydantic import BaseModel

from core.config import config


def get_module_by_model(model):
    for k, v in config.services.items():
        if v['schema'].get(model):
            return k

def recognize_type(module: str, model: str, k: str, fielinfo):
    """
    Для шаблонизатора распознаем тип для удобства HTMX (универсальные компоненты)
    """
    res = 'str'
    if k =='search':
        res = 'search'
    elif k.startswith('country'):
        res = 'country'
        model = 'country'
    elif k.startswith('phone'):
        res = 'phone'
    elif k.startswith('currency'):
        res = 'currency'
        model = 'currency'
    elif k.startswith('locale'):
        res = 'locale'
        model = 'locale'
    elif k.endswith('_id') and k not in ('external_number',):
        res = 'model'
        module = get_module_by_model(model[0:-3])
    elif k.endswith('_ids'):
        res = 'list'
    elif fielinfo.annotation == typing.Optional[datetime.datetime] or fielinfo.annotation == datetime.datetime:
        res = 'datetime'
    elif fielinfo.annotation == typing.Optional[str]:
        res = 'str'
    return {
        'type': res,
        'module': module,
        'model': model,
        'required': fielinfo.is_required(),
        'title': fielinfo.title,
        # в какие UI виджеты поле доступно filter, card, table, form
        'widget': fielinfo.json_schema_extra or {}
    }


def get_columns(module: str, model: str, schema: BaseModel, data: list = None, exclude: list[str] = []):
    """
        Метод отдает типы полей для того, что бы строить фронтенд
    """
    columns = {}
    for k, v in schema.model_fields.items():
        if k in exclude: continue
        columns.update({
            k: recognize_type(module, model, k, v)
        })
    if data:
        for row in data:
            for col, val in row.items():
                if col in exclude: continue
                row[col] = {
                    **columns[col],
                    'val': datetime.datetime.fromisoformat(val) if columns[col]['type'] == 'datetime' else val
                }
    return columns, data