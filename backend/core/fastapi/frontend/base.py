import uuid
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


class ExceptionResponseSchema(BaseModel):
    error: str


router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


class FilterSchema(BaseModel):
    model: str
    prefix: str


@router.post("/filter", response_class=HTMLResponse)
async def _filter(request: Request, filschema: FilterSchema):
    """
     Универсальный запрос, который отдает фильтр обьекта по его модулю и модели
    """
    cls = ClassView(request, filschema.model, prefix=filschema.prefix)
    return cls.get_filter()


class SearchSchema(BaseModel):
    model: str
    search: str = ''
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
            'label': i.get('title') or i.get('name') or i.get('english_name')
        }
        for i in data['data']
    ]


class SearchIds(BaseModel):
    model: str
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
            'label': i.get('title') or i.get('name') or i.get('english_name')
        }
        for i in data['data']
    ]


class TableSchema(BaseModel):
    model: str
    cursor: Optional[int] = 0
    prefix: str


@router.post("/table", response_class=HTMLResponse)
async def table(request: Request, schema: TableSchema):
    """
     Универсальный запрос, который отдает таблицу обьекта и связанные если нужно
    """
    form_data = await request.json()

    qp = request.query_params
    if form_data.get('prefix'):
        qp = clean_filter(form_data, form_data['prefix'])
        if qp:
            qp = {i: v for i, v in qp[0].items() if v}

    cls = ClassView(request, params=qp, model=schema.model, prefix=schema.prefix)
    return await cls.get_table()


class LineSchema(BaseModel):
    model: str
    prefix: str


@router.post("/table/line", response_class=HTMLResponse)
async def line(request: Request, schema: TableSchema):
    """
     Универсальный запрос, который отдает таблицу обьекта и связанные если нужно
    """
    form_data = await request.json()
    new_id = uuid.uuid4()
    qp = request.query_params
    if form_data.get('prefix'):
        qp = clean_filter(form_data, form_data['prefix'])
        if qp:
            qp = {i: v for i, v in qp[0].items() if v}
    cls = ClassView(request, params=qp, model=schema.model, prefix=f'{schema.prefix}--{new_id}--')
    return await cls.get_create_line(type='table')


class ModelSchema(BaseModel):
    model: str
    prefix: str
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
    cls = ClassView(request, schema.model)
    link_view = await cls.get_link_view(model_id=schema.id)
    return link_view


class ModalSchema(BaseModel):
    prefix: str
    model: str
    method: str
    backdrop: Optional[str] = None
    id: Optional[UUID4] = None
    target_id: str = None

    class Config:
        extra = 'allow'


@router.post("/modal", response_class=HTMLResponse)
async def modal(request: Request, schema: ModalSchema):
    """
     Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
    """
    cls = ClassView(request, schema.model)
    if data := schema.model_extra:
        _json = {}
        data = clean_filter(data, schema.prefix)
        method_schema = getattr(cls.model.schemas, schema.method)
        if data:
            try:
                method_schema_obj = method_schema(**data[0])
            except ValidationError as e:
                raise HTTPException(status_code=406, detail=f"Error: {str(e)}")
            _json = method_schema_obj.model_dump(mode='json')
        adapter_method = getattr(cls.model.adapter, schema.method)
        await adapter_method(id=schema.id, model=schema.model, json=_json)
        return cls.send_message(f'{cls.model.name.capitalize()}: is {schema.method.capitalize()}')
    else:
        model_method = getattr(cls, f'get_{schema.method}')
        return await model_method(model_id=schema.id, target_id=schema.target_id, backdrop=schema.backdrop)


class ActionSchema(BaseModel):
    prefix: str
    model: str
    action: str
    id: UUID4


    class Config:
        extra = 'allow'

@router.post("/action", response_class=HTMLResponse)
async def action(request: Request, schema: ActionSchema):
    """
     Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
    """
    cls = ClassView(request, schema.model, prefix=schema.prefix)
    func = cls.actions.get(schema.action)
    build_func = func['func']
    res = await build_func(payload=schema.model_dump_json())
    return cls.send_message(res['detail'])
