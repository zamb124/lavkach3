import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator, UUID4
from starlette.responses import JSONResponse

from core.fastapi.frontend.schema_recognizer import ModelView
from core.fastapi.frontend.uttils import clean_filter


class ExceptionResponseSchema(BaseModel):
    error: str


router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


class FilterSchema(BaseModel):
    module: str
    model: str
    prefix: str


@router.post("/filter", response_class=HTMLResponse)
async def _filter(request: Request, filschema: FilterSchema):
    """
     Универсальный запрос, который отдает фильтр обьекта по его модулю и модели
    """
    htmx_orm = ModelView(request, filschema.module, filschema.model, prefix=filschema.prefix)
    return htmx_orm.get_filter()


class SearchSchema(BaseModel):
    module: str
    model: str
    query: str = ''


@router.get("/search", response_class=JSONResponse)
async def search(request: Request, schema: SearchSchema = Depends(SearchSchema)):
    """
     Универсальный запрос поиска
    """
    params = {'search': schema.query}
    async with getattr(request.scope['env'], schema.module) as a:
        data = await a.list(params=params, model=schema.model)
    return [
        {
            'value': i['id'],
            'label': i.get('title') or i.get('name') or i.get('english_name')
        }
        for i in data['data']
    ]


class SearchIds(BaseModel):
    module: str
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
    async with getattr(request.scope['env'], schema.module) as a:
        data = await a.list(params=params, model=schema.model)
    return [
        {
            'value': i['id'],
            'label': i.get('title') or i.get('name') or i.get('english_name')
        }
        for i in data['data']
    ]


class TableSchema(BaseModel):
    module: str
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
    view = ModelView(request, params=qp, module=schema.module, model=schema.model, prefix=schema.prefix)
    return await view.get_table()


class LineSchema(BaseModel):
    module: str
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
    view = ModelView(request, params=qp, module=schema.module, model=schema.model,
                     prefix=f'{schema.prefix}--{new_id}--')
    return await view.get_create_line()


class ModelSchema(BaseModel):
    module: str
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
    model = ModelView(request, schema.module, schema.model)
    link_view = await model.get_link_view(model_id=schema.id)
    return link_view


class ModalSchema(BaseModel):
    prefix: str
    module: str
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
    model = ModelView(request, schema.module, schema.model)
    if data := schema.model_extra:
        data = clean_filter(data, schema.prefix)
        method_schema = getattr(model.schemas, schema.method)
        method_schema_obj = method_schema(**data[0])
        adapter_method = getattr(model.adapter, schema.method)
        responce = await adapter_method(id=schema.id, model=schema.model,
                                        json=method_schema_obj.model_dump(mode='json'))
        return model.send_message(f'{model.model.capitalize()}: is {schema.method.capitalize()}')
    else:
        model_method = getattr(model, f'get_{schema.method}')
        return await model_method(model_id=schema.id, target_id=schema.target_id, backdrop=schema.backdrop)
