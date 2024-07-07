import asyncio
import datetime
import uuid
from collections import defaultdict
from typing import Optional, Any, Iterable

from fastapi import HTTPException
from jinja2_fragments import render_block
from pydantic import BaseModel, ValidationError
from starlette.datastructures import QueryParams

from core.fastapi.frontend.enviroment import environment
from core.fastapi.frontend.exceptions import HTMXException
from core.fastapi.frontend.field import Fields
from core.fastapi.frontend.types import MethodType
from core.utils.timeit import timed
from core.fastapi.frontend.types import LineType


class Line(BaseModel):
    """
        Обьект описывающий обьект отданный из другого сервиса или класса с помощью Pydantic модели
    """
    type: LineType                          # Тип поля СМ LineType
    lines: 'Lines'                          # Список, которому принадлежит строка
    model_name: str                         # Имя модели
    domain_name: str                        # Наименование домена модели
    schema: Any                             # Схема обьекта
    actions: dict                           # Доступные методы обьекта
    fields: Optional['Fields'] = None       # Поля обьекта
    id: Optional[uuid.UUID] = None          # ID обьекта (если есть)
    lsn: Optional[int] = None               # LSN обьекта (если есть)
    vars: Optional[dict] = None             # vars обьекта (если есть)
    company_id: Optional[uuid.UUID] = None  # Компания обьекта (если есть обьект)
    display_title: Optional[str] = None     # Title (Поле title, или Компьют поле)
    is_last: bool = False                   # True Если обьект последний в Lines
    class_key: str                          # Уникальный ключ конструктора
    is_rel: bool = False                    # True если обьек является relation от поля родителя

    @property
    def key(self) -> str:
        """Проп генерации UI ключа для обьекта"""
        if self.type == LineType.LINE:
            key = self.id
        elif self.type == LineType.NEW:
            key = id(self)  # type: ignore
        else:
            key = self.type.value
        return f'{self.lines.key}--{key}'

    @property
    def ui_key(self) -> str:
        """Сгенерировать ключ обьекта для UI"""
        return f'{self.model_name}--{self.id}'

    @timed
    def _change_assign_line(self) -> None:
        """Присвоение нового обьекта Line'у"""
        for _, field in self.fields:  # type: ignore
            field.line = self

    @timed
    def line_copy(self, _type: LineType | None = None) -> 'Line':
        """Метод копирования лайна"""
        new_line = self.copy(deep=True)
        if _type:
            new_line.type = _type
        new_line._change_assign_line()
        if _type == LineType.NEW:
            new_line.id = uuid.uuid4()
        return new_line

    def render(self, block_name: str, method: MethodType = MethodType.GET, last=False) -> str:
        """
            block_name: имя блока в шаблоне
            edit: Редактируемые ли поля внутри или нет
        """
        try:
            rendered_html = render_block(
                environment=environment,
                template_name=f'line/line.html',
                block_name=block_name,
                method=method,
                line=self,
                last=last
            )
        except Exception as ex:
            raise
        return rendered_html

    @property
    def button_view(self) -> str:
        """Сгенерировать кнопку на просмотр обьекта"""
        return self.render('button_view')

    @property
    def button_update(self) -> str:
        """Сгенерировать кнопку на редактирование обьекта"""
        return self.render('button_update')

    @property
    def button_create(self) -> str:
        """Сгенерировать кнопку на создание обьекта"""
        return self.render('button_create')

    @property
    def button_delete(self) -> str:
        """Сгенерировать кнопку на удаление обьекта"""
        return self.render(block_name='button_delete')

    @property
    def button_save(self) -> str:
        """Кнопка сохранения обьекта"""
        return self.render(block_name='button_save')

    @property
    def button_actions(self) -> str:
        """Сгенерировать кнопку на меню доступных методов обьекта"""
        return self.render(block_name='button_actions')

    @property
    def as_tr_get(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.render(block_name='as_tr', method=MethodType.GET)

    @property
    def as_tr_header(self) -> str:
        """Отобразить обьект как строку заголовок таблицы"""
        return self.render(block_name='as_tr_header', method=MethodType.GET)

    @property
    def as_tr_update(self) -> str:
        """Отобразить обьект как строку таблицы на редактирование"""
        return self.render(block_name='as_tr', method=MethodType.UPDATE)

    @property
    def as_tr_create(self) -> str:
        """Отобразить обьект как строку таблицы на создание"""
        return self.render(block_name='as_tr', method=MethodType.CREATE)

    @property
    def as_item(self) -> str:
        """Отобразить обьект как айтем с заголовком"""
        return self.render(block_name='as_item', method=MethodType.CREATE)

    @property
    def as_div_get(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.render(block_name='as_div', method=MethodType.GET)

    @property
    def as_div_update(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.render(block_name='as_div', method=MethodType.UPDATE)

    @property
    def as_div_create(self) -> str:
        """Отобразить обьект как строку таблицы на просмотр"""
        return self.render(block_name='as_div', method=MethodType.CREATE)

    @property
    def get_update(self) -> str:
        """Метод отдает модалку на редактирование обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.UPDATE,
            block_name='modal',
            line=self
        )

    @property
    def get_get(self) -> str:
        """Метод отдает модалку на просмотр обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.GET,
            block_name='modal',
            line=self
        )

    @property
    def get_delete(self) -> str:
        """Метод отдает модалку на удаление обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.DELETE,
            block_name='delete',
            line=self,
        )

    @property
    def get_create(self) -> str:
        """Метод отдает модалку на создание нового обьекта"""
        return render_block(
            environment=environment,
            template_name=f'line/modal.html',
            method=MethodType.CREATE,
            block_name='modal',
            line=self,
        )


class FilterLine(Line):
    """Обертка для определения класса фильтра"""
    ...


class Lines(BaseModel):
    """Делаем класс похожий на List и уже работаем с ним"""
    parent_field: Optional[Any] = None    # Поле родитель, если класс конструктор это Field другого класса
    class_key: Optional[str]              # Ключ класса конструктора
    line_header: Optional[Line] = None    # Обьект для заголовка
    line_new: Optional[Line] = None       # Пустой обьект
    line_filter: Optional[Line] = None    # Обьект, описывающий фильтр
    lines: list['Line'] = []              # Список обьектов
    vars: Optional[dict] = {}             # Произвольный словарь с параметрами
    params: Optional[dict] = {}           # Параметры на вхрде
    join_related: Optional[bool] = True   # Джойнить рилейшен столбцы
    join_fields: Optional[list] = []      # Список присоединяемых полей, если пусто, значит все
    cls: Any                              # Класс конструктора ClassView

    class Config:
        arbitrary_types_allowed = True

    @property
    def key(self) -> str:
        return self.parent_field.key if self.parent_field else self.class_key

    def __bool__(self) -> bool:
        if not self.lines:
            return False
        else:
            return True

    def __deepcopy__(self, memodict={}) -> 'Lines':
        return self

    @timed
    async def get_data(
            self,
            params: QueryParams | dict | None = None,
            join_related: bool = True,
            join_fields: list | None = None,
            data: list | dict | None = None,
            **kwargs
    ) -> None:
        """Метод собирает данные для конструктора модели"""
        if not params:
            params = self.params
        if join_related:
            self.join_related = join_related
        if join_fields:
            self.join_fields = join_fields or []
        if not data:
            async with self.cls.model.adapter as a:  # type: ignore
                resp_data = await a.list(params=params)
                data = resp_data['data']
        await self.fill_lines(data, join_related, join_fields)

    @timed
    async def fill_lines(
            self,
            data: list,
            join_related: bool = False,
            join_fields: list = [],
    ) -> None:

        assert self.line_header, 'Line header is not set'
        for n, row in enumerate(data):
            line_copied = self.line_header.line_copy(_type=LineType.LINE)
            line_copied.id = row['id']
            line_copied.type = LineType.LINE
            line_copied.is_last = False
            line_copied.display_title = row.get('title')
            line_copied.company_id = row.get('company_id')
            line_copied.id = row.get('id')
            line_copied.lsn = row.get('lsn')
            for _, col in line_copied.fields:
                col.val = row[col.field_name]
                col.line = line_copied
                if col.type in ('date', 'datetime'):
                    if col.val:
                        col.val = datetime.datetime.fromisoformat(col.val)
                elif col.type == 'id':
                    if not col.val:
                        col.val = []
                elif col.type == 'enum' and col.color_map and col.val:
                    color_enum = col.enums(col.val)
                    col.color = col.color_map.get(color_enum)
                elif col.type.endswith('list_rel'):
                    print(f'rel - {col.lines.line_header.model_name}')
                    col.lines.parent_field = col
                    await col.lines.fill_lines(data=col.val, join_related=False)
            self.lines.append(line_copied)

        if join_related:
            missing_fields = defaultdict(list)
            for _line in self.lines:
                """Достаем все релейтед обьекты у которых модуль отличается"""
                assert _line.fields,   "Проверяем что все поля есть"
                for field_name, field in _line.fields:
                    if field.type in ('uuid',):
                        # if field.widget.get('table'):  # TODO: может все надо а не ток table
                        if not join_fields:
                            missing_fields[field.field_name].append((field.val, field))
                        elif field.field_name in join_fields:
                            missing_fields[field.field_name].append((field.val, field))
            to_serialize = []
            for miss_key, miss_value in missing_fields.items():
                # _data = []
                _vals, _fields = [i[0] for i in miss_value], [i[1] for i in miss_value]
                miss_value_str = ''
                _corutine_data = None
                if isinstance(_vals, list):
                    miss_value_str = ','.join([i for i in _vals if i])
                if miss_value_str:
                    qp = {'id__in': miss_value_str}
                    _corutine_data = asyncio.create_task(self.cls.env[_fields[0].model_name].adapter.list(params=qp))
                to_serialize.append((_vals, _fields, _corutine_data))
            for _vals, _fields, _corutine_data in to_serialize:
                _join_lines = {}
                if _corutine_data:
                    _data = await _corutine_data
                    _join_lines = {i['id']: i for i in _data['data']}
                for _val, _field in zip(_vals, _fields):
                    if isinstance(_val, list):
                        _new_vals = []
                        for _v in _val:
                            __val = _join_lines.get(_v)
                            if __val:
                                _new_vals.append(__val)
                        _field.val = _new_vals
                    else:
                        _field.val = _join_lines.get(_val)
                    if _field.type == 'uuid':
                        _field.type = 'rel'
                    elif _field.type == 'list_uuid':
                        _field.type = 'list_rel'
                    else:
                        raise HTMXException(
                            status_code=500,
                            detail=f'Wrong field name {_field.field_name} in table model {_field.model}'
                        )
            for col in missing_fields.keys():
                for _field_name, _header_col in self.line_header.fields:  # type: ignore
                    if col == _field_name:
                        _header_col.type = _header_col.type.replace('uuid', 'rel')
                        _header_col.type = _header_col.type.replace('list_uuid', 'list_rel')

    async def get_lines(self, ids: list[uuid.UUID], join_related: bool = False) -> list[Line]:
        await self.get_data(
            schema=self.cls.model.schemas.get,
            params={'id__in': ids},
            join_related=join_related or self.join_related,
            join_fields=self.join_fields,
        )
        return self.lines

    async def update_lines(self, data: dict, id: uuid.UUID) -> list[Line]:
        """Метод обновления обьектов"""
        new_data = []
        for raw_line in data:
            try:
                method_schema_obj = self.cls.model.schemas.update(**raw_line)
            except ValidationError as e:
                raise HTTPException(status_code=406, detail=f"Error: {str(e)}")
            _json = method_schema_obj.model_dump(mode='json', exclude_unset=True)
            line = await self.cls.model.adapter.update(id=id, json=_json)
            new_data.append(line)
        await self.fill_lines(new_data)
        return self.lines

    async def create_lines(self, data: dict) -> list[Line]:
        """Метод создания обьектов"""
        new_data = []
        for raw_line in data:
            try:
                method_schema_obj = self.cls.model.schemas.create(**raw_line)
            except ValidationError as e:
                raise HTTPException(status_code=406, detail=f"Error: {str(e)}")
            _json = method_schema_obj.model_dump(mode='json', exclude_unset=True)
            line = await self.cls.model.adapter.create(json=_json)
            new_data.append(line)
        await self.fill_lines(new_data)
        return self.lines

    async def delete_lines(self, ids: list[uuid.UUID]) -> bool:
        """Метод удаления обьектов"""
        for _id in ids:
            await self.cls.model.adapter.delete(id=_id)
        return True

    @property
    def as_table_update(self) -> str:
        """Метод отдает список обьектов как таблицу на редактирование"""
        rendered_html = ''
        for i, line in enumerate(self.lines):
            if i == len(self.lines) - 1:
                line.is_last = True
            rendered_html += line.as_tr_update
        return rendered_html

    @property
    def as_table_get(self) -> str:
        """Метод отдает список обьектов как таблицу на просмотр"""
        rendered_html = ''
        for i, line in enumerate(self.lines):
            if i == len(self.lines) - 1:
                line.is_last = True
            rendered_html += line.as_tr_get
        return rendered_html

    @property
    def as_table_header(self) -> str:
        return self.line_header.as_tr_header  # type: ignore
