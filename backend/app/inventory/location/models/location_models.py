import uuid
from email.policy import default
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Sequence, Uuid, ForeignKey, text, JSON, select
from sqlalchemy.orm import mapped_column, Mapped, relationship, column_property, aliased, joinedload
from watchfiles import awatch

from app.inventory.location.enums import LocationClass, PutawayStrategy, BlockerEnum, LocationErrors
from app.inventory.mixins import LocationMixin
from core.db import Base, session
from core.db.mixins import AllMixin
from core.db.types import ids
from core.exceptions.module import ModuleException
if TYPE_CHECKING:
    from app.inventory.location.models.location_models import LocationType
    from app.inventory.quant.models import Quant

# Словарь разрешенных классов локаций для каждого класса локации
location_class_hierarchy_allowed = {
    LocationClass.ZONE: [LocationClass.ZONE, LocationClass.PLACE, LocationClass.PACKAGE,LocationClass.RESOURCE], # Зона может содержать зону, ячейки, упаковки, и ресурсы
    LocationClass.PACKAGE: [LocationClass.PACKAGE],  # Упаковка содержать другую упаковку
    LocationClass.PLACE: [LocationClass.PACKAGE,],  # Ячейка может быть только в зоне
    LocationClass.RESOURCE: [LocationClass.PACKAGE],  # Ресурс может быть только в зоне
}
location_class_allowed_none_parent = [
    LocationClass.ZONE,  # Зона может быть корневой
    LocationClass.PARTNER,
    LocationClass.INVENTORY,
    LocationClass.SCRAPPED,
    LocationClass.SCRAP,
    LocationClass.LOST
]

def default_capacity(context):
    if context.get_current_parameters()['location_class'] == LocationClass.PACKAGE:
        return 25
    return 100

class LocationType(Base, AllMixin, LocationMixin):
    """
    Типы местоположения - Обозначают набор свойств местоположения, например Паллет, или ячейка, или ящик, или зона.

    Атрибуты:
        title (str): Название типа местоположения.
        store_id (Optional[uuid.UUID]): Идентификатор магазина.
        allowed_package_type_ids (Optional[ids]): Разрешенные типы упаковок.
        exclude_package_type_ids (Optional[ids]): Исключенные типы упаковок.
        is_homogeneity (Optional[bool]): Запрет на 1KU 2х разных партий.
        strategy (Optional[PutawayStrategy]): Стратегия комплектования.
        is_can_negative (Optional[bool]): Может иметь отрицательный остаток.
        capacity (Optional[int]): # Условная единица вместимости, у обычных ячеек она
            обычно, 100, но может быть и меньше и больше и означает сколько уловных единиц может вместить такой тп ячеек
            можно установить 999, тогда ячейка считается безразмерной
            , но у Упаковок (Package) нужно услатавливать такую, сколько она поглотит
            условных едницы, Например, 3 упаковки в ячейке, значит упаковка имеет вместимость 33,33% от ячейки. ее
            Условие вместимости 33, у ячейки 100, значит 3 таких упаковки могут вместится в ячейку, или например ячейка
            размером Под 1 паллет, значит капасити паллета 100, а у ячейки 100, значит 1 ячейка вмещает 1 паллет.
    """
    __tablename__ = "location_type"
    lsn_seq = Sequence(f'location_type_lsn_seq')
    title: Mapped[str] = mapped_column(index=True)
    store_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True)
    allowed_package_type_ids: Mapped[Optional[ids]] = mapped_column(index=True)  # Разрешенные типы упаковок
    exclude_package_type_ids: Mapped[Optional[ids]] = mapped_column(index=True)  # Исключение типы упаковок
    is_homogeneity: Mapped[Optional[bool]] = mapped_column(default=False, index=True)  # Запрет на 1KU 2х разных партий
    strategy: Mapped[Optional['PutawayStrategy']] = mapped_column(default=PutawayStrategy.FEFO)  # Стратегия комплектования
    is_can_negative: Mapped[Optional[bool]] = mapped_column(server_default=text('false'), index=True)  # Может иметь отрицательный остаток
    capacity: Mapped[int] = mapped_column(default=default_capacity, index=True)
    storage_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('storage_type.id'), index=True)


class Location(Base, AllMixin):
    """
    **Местоположение** - это объект, хранящий в себе кванты, а также другие локации.
    Атрибуты:
        title (str): Название местоположения/или идентификатор.
        store_id (uuid.UUID): Идентификатор магазина.
        location_class (LocationClass): Класс местоположения.
        location_type_id (uuid.UUID): Идентификатор типа местоположения.
        location_type_rel (Optional[LocationType]): Связь с типом местоположения.
        location_id (Optional[uuid.UUID]): Идентификатор родительского местоположения.
        zone_id (Optional[uuid.UUID]): Идентификатор зоны.
        is_active (Optional[bool]): Активность местоположения.
        block (BlockerEnum): Статус блокир��вки местоположения.
    """
    __tablename__ = "location"
    lsn_seq = Sequence(f'location_lsn_seq')
    title: Mapped[str] = mapped_column(index=True)
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    location_class: Mapped[LocationClass] = mapped_column(index=True)
    location_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('location_type.id'), index=True)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id"), index=True)
    location_type_rel: Mapped[Optional[LocationType]] = relationship(lazy="noload")
    is_active: Mapped[Optional[bool]] = mapped_column(default=True)
    block: Mapped[BlockerEnum] = mapped_column(default=BlockerEnum.FREE, index=True)
    sort: Mapped[int] = mapped_column(default=0, index=True)
    child_locations_rel: Mapped[Optional[list['Location']]] = relationship(lazy="noload")
    quants_rel: Mapped[Optional[list['Quant']]] = relationship(
        'Quant',
        primaryjoin='Location.id == Quant.location_id',
        foreign_keys='Quant.location_id',
        lazy = 'noload'
    )

    @classmethod
    def get_query_locations_by_zone_ids(cls, location_ids, location_classes=None, location_type_ids=None):
        """
            Метод отдает дополнительный query, который позволяет получить все местоположения по зонам,
            классам локаций и типам локаций
        """
        location_cte = (
            select(
                Location.id,
                Location.location_id,
                Location.location_class,
                Location.location_type_id,
            )
            .where(Location.id.in_(location_ids))
            .cte(name="location_cte", recursive=True)
        )

        # Определяем алиас для CTE
        location_alias = aliased(location_cte)

        # Добавляем рекурсивную часть запроса
        location_cte = location_cte.union_all(
            select(
                Location.id,
                Location.location_id,
                Location.location_class,
                Location.location_type_id,
            )
            .where(Location.location_id == location_alias.c.id)
            .where(Location.location_class.in_(location_classes) if location_classes else True)  # type: ignore
            .where(Location.location_type_id.in_(location_type_ids) if location_type_ids else True)  # type: ignore
        )
        # Создаем условное выражение для сортировки
        # Выполняем запрос
        return (
            select(Location)
            .options(joinedload(Location.location_type_rel))
            .where(Location.id.in_(select(location_cte.c.id)))
        )

    async def parent_validate(self, parent_location: Optional['Location'] = None):
        if parent_location:
            allowed_classes = location_class_hierarchy_allowed.get(parent_location.location_class, [])
            if not self.location_class in allowed_classes:
                raise ModuleException(status_code=406, enum=LocationErrors.LOCATION_CLASS_NOT_ALLOWED)
            if self.location_class == LocationClass.PACKAGE:
                if not self.location_type_id in parent_location.location_type_rel.allowed_package_types:
                    raise ModuleException(status_code=406, enum=LocationErrors.LOCATION_TYPE_NOT_ALLOWED)
        else:
            if self.location_class not in location_class_allowed_none_parent:
                raise ModuleException(status_code=406, enum=LocationErrors.LOCATION_CLASS_NOT_ALLOWED)

class LocationLog(Base, AllMixin):
    """
    **Лог местоположения** - это объект, хранящий в себе историю изменения местоположения.
    Атрибуты:
        location_id (uuid.UUID): Идентификатор местоположения.
        location_id_rel (Optional[Location]): Связь с местоположением.
        title (str): Название местоположения/или идентификатор.
        store_id (uuid.UUID): Идентификатор магазина.
        location_class (LocationClass): Класс местоположения.
        location_type_id (uuid.UUID): Идентификатор типа местополо��ения.
        location_type_rel (Optional[LocationType]): Связь с типом местоположения.
        location_id (Optional[uuid.UUID]): Идентификатор родительского местоположения.
        zone_id (Optional[uuid.UUID]): Идентификатор зоны.
        is_active (Optional[bool]): Активность местоположения.
        block (BlockerEnum): Статус блокировки местоположения.
    """
    __tablename__ = "location_log"
    lsn_seq = Sequence(f'location_log_lsn_seq')
    title: Mapped[str] = mapped_column(index=True)
    store_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    location_class: Mapped[LocationClass] = mapped_column(index=True)
    location_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('location_type.id'), index=True)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("location.id"), index=True)
    location_type_rel: Mapped[Optional[LocationType]] = relationship(lazy="noload")
    is_active: Mapped[Optional[bool]] = mapped_column(default=True)
    block: Mapped[BlockerEnum] = mapped_column(default=BlockerEnum.FREE, index=True)