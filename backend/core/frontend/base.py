import logging
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
from app.front.utills import BaseClass
from core.frontend.constructor import ClassView, get_view, BaseSchema, Method
from core.frontend.utils import clean_filter
from fastapi import FastAPI, File, UploadFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExceptionResponseSchema(BaseModel):
    error: str



router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)

@router.post("/filter", response_class=HTMLResponse)
async def _filter(cls: ClassView = Depends(get_view)):
    """
     Универсальный запрос, который отдает фильтр обьекта по его модулю и модели
    """
    return cls.h.as_filter_get


class SearchSchema(BaseModel):
    model: str
    search: str = ''
    filter: Optional[Any] = None
    key: Optional[str] = None

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
async def search(request: Request, schema: SearchSchema = Depends()):
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


class SearchIds(BaseModel):
    model: str
    id__in: str


@router.get("/get_by_ids", response_class=JSONResponse)
async def get_by_ids(request: Request, schema: SearchIds = Depends()):
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
async def table(view: ClassView = Depends(get_view)):
    """
     Универсальный запрос, который отдает таблицу обьекта и связанные если нужно
    """
    await view.init()
    return view.h.as_table_get


class LineSchema(BaseSchema):
    id: Optional[UUID4 | int] = None
    mode: Optional[str] = 'get'

    class Config:
        extra = "allow"


@router.post("/line", response_class=HTMLResponse)
async def line(cls: ClassView = Depends(get_view)):
    """
     Универсальный запрос, который отдает/изменяет обьект
    """
    match cls.v.schema.method:
        case Method.UPDATE:
            """Отдать обьект на редактирование, в зависимости от mode (tr/div)"""
            line = await cls.get_lines(ids=[cls.v.schema.id], join_related=False)
            return getattr(line.h, f'as_{cls.v.schema.mode}_update')
        case Method.GET:
            """Отдать обьект на чтение, в зависимости от mode (tr/div)"""
            line = await cls.get_lines(ids=[cls.v.schema.id], join_related=False)
            return getattr(line.h, f'as_{cls.v.schema.mode}_get')
        case Method.CREATE:
            """Отдать обьект на создание, в зависимости от mode (tr/div)"""
            return cls.h.as_tr_create
        case Method.DELETE:
            """Отдать обьект на удаление, в не зависимости от mode (tr/div)"""
            if isinstance(cls.v.schema.id, int):
                """Если это временная запись, то просто удалить"""
                return
            line = await cls.get_lines(ids=[cls.v.schema.id], join_related=False)
            return line.h.as_modal_delete
        case Method.UPDATE_SAVE:
            """Сохранение записи при измененнии"""
            data = clean_filter(cls.v.schema.model_extra, cls.v.schema.key)
            await cls.update_lines(id=cls.v.schema.id, data=data)
        case Method.CREATE_SAVE:
            """Сохранение записи при создании"""
            data = clean_filter(cls.v.schema.model_extra, cls.v.schema.key)
            line = await cls.create_lines(data)
            return line.h.as_div_update
        case Method.DELETE_SAVE:
            await cls.delete_lines(ids=[cls.v.schema.id])
            """Отдать обьект на удаление, в не зависимости от mode (tr/div)"""


class ModalSchema(BaseSchema):
    id: Optional[UUID4] = None

    class Config:
        extra = 'allow'

@router.post("/modal", response_class=HTMLResponse)
async def modal(cls: ClassView = Depends(get_view)):
    """
     Универсальный запрос модалки, который отдает форму модели
    """
    cls.reset_key()
    match cls.v.schema.method:
        case Method.GET:
            line = await cls.get_lines(ids=[cls.v.schema.id])
            return line.h.as_modal_get
        case Method.UPDATE:
            line = await cls.get_lines(ids=[cls.v.schema.id])
            return line.h.as_modal_update
        case Method.DELETE:
            line = await cls.get_lines(ids=[cls.v.schema.id])
            return line.h.as_modal_delete
        case Method.CREATE:
            return cls.h.as_modal_create


class ActionSchema(BaseSchema):
    action: str
    ids: Optional[list[str]] = []
    schema: Any = None
    commit: Optional[bool] = False

    class Config:
        extra = 'allow'


@router.post("/action", response_class=HTMLResponse)
async def action(cls: ClassView = Depends(get_view)):
    """
     Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
    """
    func: Callable = getattr(cls.v.model.adapter, cls.v.schema.action)
    result = []
    if cls.v.schema.commit and cls.v.schema.method == 'update':
        action_schema = cls.v.actions[cls.v.schema.action]['schema']
        if data := cls.v.schema.model_extra:
            _json: dict = {}
            data = clean_filter(data, cls.v.schema.key)
            for line in data:  # type: ignore
                obj = action_schema(**line)
                res = await func(obj)
                result += res
        return cls.send_message(message=f'Action {cls.v.schema.action} done')
    elif cls.v.schema.method == 'update':
        res = await func(payload=cls.v.schema.model_dump_json())
        return cls.send_message(message=f'Action {cls.v.schema.action} done')
    elif cls.v.schema.method == 'get':
        action_schema = cls.v.actions[cls.v.schema.action]['schema']
        return await cls.get_action(action=cls.v.schema.action, ids=cls.v.schema.ids, schema=action_schema)

    return cls.send_message('Action Done')

class ImportSchema(BaseSchema):
    class Config:
        extra = 'allow'

@router.post("/import", response_class=HTMLResponse)
async def modal(cls: ClassView = Depends(get_view)):
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
async def import_upload(cls: ClassView = Depends(get_view)):
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


