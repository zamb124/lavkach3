import json
import uuid
from enum import Enum
from typing import Optional, Any

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator, UUID4, model_validator
from pydantic_core import ValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from core.fastapi.frontend.uttils import clean_filter




class Method(str, Enum):
    GET:    str = 'get'
    CREATE: str = 'create'
    UPDATE: str = 'update'
    DELETE: str = 'update'


class ExceptionResponseSchema(BaseModel):
    error: str


class BaseSchema(BaseModel):
    """
        Обязательные моля всегда чц
    """
    model: str
    key: str
    method: Method



router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


class FilterSchema(BaseSchema):
    model: str
    key: str


@router.post("/filter", response_class=HTMLResponse)
async def _filter(request: Request, filschema: FilterSchema):
    """
     Универсальный запрос, который отдает фильтр обьекта по его модулю и модели
    """
    cls = await ClassView(request, filschema.model, key=filschema.key)
    return cls.as_filter


class SearchSchema(BaseSchema):
    model: str
    search: str = ''
    method: Optional[Method] = None
    key: Optional[str] = None
    filter: Optional[Any] = None

    @model_validator(mode='before')
    def _filter(cls, value):
        """
            Так же убираем все пустые params
        """

        if f:=value.get('filter'):
            if isinstance(f, str):
                try:
                    value['filter'] = eval(f)
                except TypeError as ex:
                    raise 'Type Error'
        return value


@router.get("/search", response_class=JSONResponse)
async def search(request: Request, schema: SearchSchema = Depends(SearchSchema)):
    """
     Универсальный запрос поиска
    """
    params = {'search': schema.search}
    if schema.filter:
        params.update(schema.filter)
    async with request.scope['env'][schema.model].adapter as a:
        data = await a.list(params=params, model=schema.model)
    return [
        {
            'value': i['id'],
            'label': i.get('title') or i.get('name') or i.get('english_name') or i.get('nickname')
        }
        for i in data['data']
    ]


class SearchIds(BaseSchema):
    model: str
    key: Optional[str] = None
    method: Optional[Method] = None
    id__in: str


@router.get("/get_by_ids", response_class=JSONResponse)
async def get_by_ids(request: Request, schema: SearchSchema = Depends(SearchIds)):
    """
     Универсальный запрос поиска
    """
    if not schema.id__in:
        return []
    params = {'id__in': schema.id__in}
    async with request.scope['env'][schema.model].adapter as a:
        data = await a.list(params=params, model=schema.model)
    return [
        {
            'value': i['id'],
            'label': i.get('title') or i.get('name') or i.get('english_name') or i.get('nickname')
        }
        for i in data['data']
    ]


class TableSchema(BaseSchema):
    model: str
    cursor: Optional[int] = 0
    key: str


@router.post("/table", response_class=HTMLResponse)
async def table(request: Request, schema: TableSchema):
    """
     Универсальный запрос, который отдает таблицу обьекта и связанные если нужно
    """
    form_data = await request.json()

    qp = request.query_params
    if form_data.get('key'):
        qp = clean_filter(form_data, form_data['key'])
        if qp:
            qp = {i: v for i, v in qp[0].items() if v}

    cls = await ClassView(request, params=qp, model=schema.model, key=schema.key, force_init=True)
    if request.query_params.get('edit'):
        return cls.as_table_form
    else:
        return cls.as_table


class LineSchema(BaseSchema):
    model: str
    key: str


@router.post("/table/line/add", response_class=HTMLResponse)
async def line(request: Request, schema: TableSchema):
    """
     Универсальный запрос, который отдает таблицу обьекта и связанные если нужно
    """
    form_data = await request.json()
    new_id = uuid.uuid4()
    qp = request.query_params
    if form_data.get('key'):
        qp = clean_filter(form_data, form_data['key'])
        if qp:
            qp = {i: v for i, v in qp[0].items() if v}
    cls = await ClassView(request, params=qp, model=schema.model, key=schema.key)
    return cls.new.as_tr_add


class ModelSchema(BaseSchema):
    model: str
    key: str
    id: UUID4

    @field_validator('id')
    @classmethod
    def id_validate(cls, val):
        return val


@router.post("/model_id", response_class=HTMLResponse)
async def model_id(request: Request, schema: ModelSchema):
    """
     отдает простой контрол для чтения
    """
    form_data = await request.json()
    cls = await ClassView(request, schema.model, force_init=False)
    link_view = await cls.get_link_view(model_id=schema.id)
    return link_view


class ModalSchema(BaseSchema):
    id: Optional[UUID4] = None

    class Config:
        extra = 'allow'



@router.post("/modal", response_class=HTMLResponse)
async def modal(request: Request, schema: ModalSchema):
    """
     Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
    """
    cls = await ClassView(request, schema.model, key=schema.key, force_init=False)
    if data := schema.model_extra:
        _json = {}
        data = clean_filter(data, schema.key)
        method_schema = getattr(cls.model.schemas, schema.method)
        if data:
            try:
                method_schema_obj = method_schema(**data[0])
            except ValidationError as e:
                raise HTTPException(status_code=406, detail=f"Error: {str(e)}")
            _json = method_schema_obj.model_dump(mode='json', exclude_unset=True)
        adapter_method = getattr(cls.model.adapter, schema.method.value)
        await adapter_method(id=schema.id, model=schema.model, json=_json)
        return cls.send_message(f'{cls.model.name.capitalize()}: is {schema.method.capitalize()}')
    else:
        if schema.method == 'create':
            #await cls.init(params={'id__in': schema.id})
            return getattr(cls.new, f'get_{schema.method.value}')
        await cls.init(params={'id__in': schema.id})
        line = cls.lines.lines[0]
        return getattr(line, f'get_{schema.method.value}')


class ActionSchema(BaseSchema):
    action: str
    ids: Optional[list[UUID4]] = []
    schema: Any = None
    commit: Optional[bool] = False


    class Config:
        extra = 'allow'

@router.post("/action", response_class=HTMLResponse)
async def action(request: Request, schema: ActionSchema):
    """
     Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
    """
    cls = await ClassView(request, schema.model)
    func = getattr(cls.model.adapter, schema.action)
    result = []
    if schema.model_extra and schema.method =='update':
        action_schema = cls.actions[schema.action]['schema']
        if data := schema.model_extra:
            _json = {}
            data = clean_filter(data, schema.key)
            for line in data:
                obj = action_schema(**line)
                res = await func(obj)
                result += res
    elif schema.method == 'update':
        res = await func(payload=schema.model_dump_json())
        return cls.send_message(res['detail'])
    elif schema.method == 'get':
        action_schema = cls.actions[schema.action]['schema']
        return await cls.get_action(action=schema.action, ids=schema.ids, schema=action_schema)

    return cls.send_message('Action Done')
