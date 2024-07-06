from enum import Enum
from typing import Optional, Any

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator, UUID4, model_validator
from starlette.responses import JSONResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from core.fastapi.frontend.uttils import clean_filter


class Method(str, Enum):
    GET: str = 'get'  # Дать запись на чтение
    CREATE: str = 'create'  # Дать запись на создание
    UPDATE: str = 'update'  # Дать запись на изменение
    DELETE: str = 'delete'  # Дать запись на удаление
    SAVE: str = 'save'  # Сохранить изменения
    SAVE_CREATE: str = 'save_create'  # Сохранить новую запись
    DELETE_DELETE: str = 'delete_delete'  # Подтвердить удаление записи


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

        if f := value.get('filter'):
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

    cls = await ClassView(request, model=schema.model, key=schema.key)
    await cls.init(params=qp, join_related=False)
    if request.query_params.get('edit'):
        return cls.as_table_form
    else:
        return cls.as_table


class LineSchema(BaseSchema):
    id: Optional[UUID4] = None
    mode: Optional[str] = 'get'

    class Config:
        extra = "allow"


@router.post("/line", response_class=HTMLResponse)
async def line(request: Request, schema: LineSchema):
    """
     Универсальный запрос, который отдает/изменяет обьект
    """
    cls = await ClassView(request, model=schema.model, key=schema.key)
    if schema.method == Method.UPDATE:
        """Отдать обьект на редактирование, в зависимости от mode (tr/div)"""
        lines = await cls.lines.get_lines(ids=[schema.id], join_related=True)
        return getattr(lines[0], f'as_{schema.mode}_update')
    elif schema.method == Method.GET:
        """Отдать обьект на чтение, в зависимости от mode (tr/div)"""
        lines = await cls.lines.get_lines(ids=[schema.id], join_related=True)
        return getattr(lines[0], f'as_{schema.mode}_get')
    elif schema.method == Method.CREATE:
        """Отдать обьект на создание, в зависимости от mode (tr/div)"""
        return cls.lines.line_new.as_tr_create
    elif schema.method == Method.DELETE:
        """Отдать обьект на удаление, в не зависимости от mode (tr/div)"""
        lines = await cls.lines.get_lines(ids=[schema.id], join_related=False)
        return lines[0].get_delete
    elif schema.method == Method.DELETE_DELETE:
        """Отдать обьект на удаление, в не зависимости от mode (tr/div)"""
    elif schema.method == Method.SAVE:
        """Сохранение записи при измененнии"""
        data = clean_filter(schema.model_extra, schema.key)
        await cls.lines.update_lines(id=schema.id, data=data)
    elif schema.method == Method.SAVE_CREATE:
        """Сохранение записи при создании"""
        data = clean_filter(schema.model_extra, schema.key)
        lines = await cls.lines.create_lines(data)
        return lines[0].as_div_update


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
    cls = await ClassView(request, schema.model, force_init=False)
    link_view = await cls.get_link_view(model_id=schema.id)
    return link_view


class ModalSchema(BaseSchema):
    id: Optional[UUID4] = None
    class_key: Optional[str] = None

    class Config:
        extra = 'allow'


@router.post("/modal", response_class=HTMLResponse)
async def modal(request: Request, schema: ModalSchema):
    """
     Универсальный запрос модалки, который отдает форму модели
    """
    cls = await ClassView(request, schema.model, force_init=False)
    match schema.method:
        case Method.GET:
            lines = await cls.lines.get_lines(ids=[schema.id], join_related=True)
            return lines[0].get_get
        case Method.UPDATE:
            lines = await cls.lines.get_lines(ids=[schema.id], join_related=True)
            return lines[0].get_update
        case Method.DELETE:
            lines = await cls.lines.get_lines(ids=[schema.id], join_related=False)
            return lines[0].get_delete
        case Method.CREATE:
            return cls.lines.line_new.get_create


class ActionSchema(BaseSchema):
    action: str
    ids: Optional[list[str]] = []
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
    if schema.commit and schema.method == 'update':
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
