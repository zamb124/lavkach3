from enum import Enum
from typing import Optional, Any, Callable
import io

import openpyxl
from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, UUID4, model_validator
from starlette.responses import JSONResponse

from app.front.front_tasks import import_prepare_data, import_save
from core.frontend.constructor import ClassView
from core.frontend.utils import clean_filter
from fastapi import FastAPI, File, UploadFile

class Method(str, Enum):
    GET: str = 'get'  # Дать запись на чтение
    CREATE: str = 'create'  # Дать запись на создание
    UPDATE: str = 'update'  # Дать запись на изменение
    DELETE: str = 'delete'  # Дать запись на удаление
    UPDATE_SAVE: str = 'save'  # Сохранить изменения
    CREATE_SAVE: str = 'save_create'  # Сохранить новую запись
    DELETE_SAVE: str = 'delete_delete'  # Подтвердить удаление записи


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
    cls = ClassView(request, filschema.model, key=filschema.key)
    return cls.as_filter


class SearchSchema(BaseSchema):
    model: str
    search: str = ''
    filter: Optional[Any] = None
    key: Optional[str] = None
    method: Optional[Method] = Method.GET

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
    id__in: str
    key: Optional[str] = None  # type: ignore
    method: Method = Method.GET


@router.get("/get_by_ids", response_class=JSONResponse)
async def get_by_ids(request: Request, schema: SearchIds = Depends(SearchIds)):
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
    def_lsn = 9999999999999999999
    qp = request.query_params
    if form_data.get('key'):
        qp = clean_filter(form_data, form_data['key'])
        if qp:
            qp = {i: v for i, v in qp[0].items() if v}  # type: ignore

    cls = ClassView(request, model=schema.model, key=schema.key)
    await cls.init(params=qp, join_related=True)
    if request.query_params.get('edit'):
        return cls.as_table_update
    else:
        return cls.as_table


class LineSchema(BaseSchema):
    id: Optional[UUID4 | int] = None
    mode: Optional[str] = 'get'

    class Config:
        extra = "allow"


@router.post("/line", response_class=HTMLResponse)
async def line(request: Request, schema: LineSchema):
    """
     Универсальный запрос, который отдает/изменяет обьект
    """
    cls = ClassView(request, model=schema.model, key=schema.key)
    match schema.method:
        case Method.UPDATE:
            """Отдать обьект на редактирование, в зависимости от mode (tr/div)"""
            lines = await cls.lines.get_lines(ids=[schema.id], join_related=True)
            return getattr(lines[0], f'as_{schema.mode}_update')
        case Method.GET:
            """Отдать обьект на чтение, в зависимости от mode (tr/div)"""
            lines = await cls.lines.get_lines(ids=[schema.id], join_related=True)
            return getattr(lines[0], f'as_{schema.mode}_get')
        case Method.CREATE:
            """Отдать обьект на создание, в зависимости от mode (tr/div)"""
            return cls.lines.line_new.as_tr_create
        case Method.DELETE:
            """Отдать обьект на удаление, в не зависимости от mode (tr/div)"""
            if isinstance(schema.id, int):
                """Если это временная запись, то просто удалить"""
                return
            lines = await cls.lines.get_lines(ids=[schema.id], join_related=False)
            return lines[0].get_delete
        case Method.UPDATE_SAVE:
            """Сохранение записи при измененнии"""
            data = clean_filter(schema.model_extra, schema.key)
            await cls.lines.update_lines(id=schema.id, data=data)
        case Method.CREATE_SAVE:
            """Сохранение записи при создании"""
            data = clean_filter(schema.model_extra, schema.key)
            lines = await cls.lines.create_lines(data)
            return lines[0].as_div_update
        case Method.DELETE_SAVE:
            await cls.lines.delete_lines(ids=[schema.id])
            """Отдать обьект на удаление, в не зависимости от mode (tr/div)"""


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
    cls = ClassView(request, schema.model, force_init=False)
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
    cls: ClassView = ClassView(request, schema.model)
    func: Callable = getattr(cls.model.adapter, schema.action)
    result = []
    if schema.commit and schema.method == 'update':
        action_schema = cls.actions[schema.action]['schema']
        if data := schema.model_extra:
            _json: dict = {}
            data = clean_filter(data, schema.key)
            for line in data:  # type: ignore
                obj = action_schema(**line)
                res = await func(obj)
                result += res
    elif schema.method == 'update':
        res = await func(payload=schema.model_dump_json())
        return cls.send_message(message=f'Action {schema.action} done')
    elif schema.method == 'get':
        action_schema = cls.actions[schema.action]['schema']
        return await cls.get_action(action=schema.action, ids=schema.ids, schema=action_schema)

    return cls.send_message('Action Done')

class ImportSchema(BaseSchema):
    class Config:
        extra = 'allow'

@router.post("/import", response_class=HTMLResponse)
async def modal(request: Request, schema: ImportSchema = None):
    """
     Универсальный запрос модалки, который отдает форму модели
    """
    cls = ClassView(request, schema.model, force_init=False)
    match schema.method:
        case Method.GET:
            return cls.get_import
        case Method.UPDATE_SAVE:
            data = clean_filter(schema.model_extra, schema.key)
            lines = await import_save(cls.model_name, data)
            await cls.init(params={}, data=lines, join_related=True)
            return cls.as_table

@router.post("/import_upload", response_class=HTMLResponse)
async def modal(request: Request, file: UploadFile):
    """
     Универсальный запрос модалки, который отдает форму модели
    """
    model, key = request.query_params.values()
    cls: ClassView = ClassView(request, model, key=key, force_init=False)
    format: str = file.filename.split('.')[-1]
    data: list = []
    header: list = []
    import_schema: BaseSchema = cls.model.schemas.create
    match format:
        case 'csv':
            ...
        case 'xlsx':
            # Read it, 'f' type is bytes
            f = await file.read()
            xlsx = io.BytesIO(f)
            wb = openpyxl.load_workbook(xlsx)
            ws = wb[wb.sheetnames[0]]

            for i, cells in enumerate(ws.iter_rows()):
                if i == 0:
                   header = [cell.value.lower() for cell in cells]
                   continue
                line: dict = {}
                for col, label in enumerate(header):
                    line[label] = cells[col].value
                data.append(line)
    if not data:
        return f"{cls.send_message(message=f'No data in file')} {cls.get_import}"
    task = await import_prepare_data.kiq(model=cls.model_name, data=data)
    task_result = await task.wait_result()
    cls.errors = task_result.return_value[0]
    lines = task_result.return_value[1]
    if task_result.return_value[2] == 'update':
        import_schema = cls.model.schemas.update
    await cls.init(data=lines, schema=import_schema)
    return f"{cls.get_import_errors}\n{cls.as_table_update}"


