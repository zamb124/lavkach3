from enum import Enum


class PutawayStrategy(str, Enum):
    FEFO: str = 'fefo'
    FIFO: str = 'fifo'
    LIFO: str = 'lifo'
    LEFO: str = 'lefo'


class LocationClass(str, Enum):
    """
    **Классификация** типов местоположения, обозначающий свойства типов местоположения
    - partner - Зона внешняя (например поставщика товаров)
    - place - Статичный класс местоположения в пространстве, например ячейка на складе или магазине
    - zone  -  ОБЬЕДИНЕНИЕ ЯЧЕЕК, и только ZONE является агрегатором и никто иной ZONE может быть родителем или являтся дочкой только ZONE, которая отвечает за агрегацию свойств местоположений, например стратегия приемки или отгрузки
    - resource - Статически/динамическое местоположение означающее ресурс с помощью которого происзодит перемещение, например Тележка, или штабелер или что то иное
    - package - Динамическое местоположение, например паллета коробка
    - lost - класс типа местоположения отвечающий аккумулирование расхождений в рамках набора локаций, может быть ограничен зоной, магазином или компанией
    - inventory - класс типов ячеек, которы аккумулирует расхождения при легальной инвентаризации
    - scrap - класс хранение некондиционного товара
    - scraped - списанный товар (уже утиилизарованный)
    -
    """
    PARTNER: str = "partner"
    PLACE: str = "place"
    RESOURCE: str = "resource"
    PACKAGE: str = "package"
    ZONE: str = "zone"
    LOST: str = "lost"
    INVENTORY: str = "inventory"
    SCRAP: str = "scrap"
    SCRAPPED: str = "scrapped"


class VirtualLocationZones(str, Enum):
    """ Виртуальные классы локаций"""
    PARTNER: str = "partner"  # Зона внешняя (например поставщика товаров)
    LOST: str = "lost"  # Класс типа местоположения отвечающий аккумулирование расхождений в рамках набора склада
    INVENTORY: str = "inventory"  # Класс типов ячеек, которы аккумулирует расхождения при легальной инвентаризации
    SCRAPPED: str = "scrapped"  # Списанный товар (уже утиилизарованный)\


class PhysicalLocationZones(str, Enum):
    """ Виртуальные классы локаций"""
    ZONE: str = "zone"
    SCRAP: str = "scrap"  # Класс хранение некондиционного товара


class ZonesVirtPhis(str, Enum):
    """ Все классы локаций, которые могут быть зонами"""
    PARTNER: str = "partner"  # Зона внешняя (например поставщика товаров)
    LOST: str = "lost"  # Класс типа местоположения отвечающий аккумулирование расхождений в рамках набора склада
    INVENTORY: str = "inventory"  # Класс типов ячеек, которы аккумулирует расхождения при легальной инвентаризации
    SCRAPPED: str = "scrapped"  # Списанный товар (уже утиилизарованный)\
    ZONE: str = "zone"
    SCRAP: str = "scrap"  # Класс хранение некондиционного товара


class PhysicalLocationClass(str, Enum):
    """
        Физические классы локаций
    """
    PLACE: str = "place"  # Статичный класс местоположения в пространстве, например ячейка на складе или магазине
    RESOURCE: str = "resource"  # Статически/динамическое местоположение означающее ресурс с помощью которого происзодит перемещение, например Тележка, или штабелер или что то иное
    PACKAGE: str = "package"  # Динамическое местоположение, например паллета коробка
    ZONE: str = "zone"
    SCRAP: str = "scrap"  # Класс хранение некондиционного товара


class PhysicalStoreLocationClass(str, Enum):
    """ Физические классы локаций хранения товаров, не катаются туда сюда"""
    PLACE: str = "place"  # Статичный класс местоположения в пространстве, например ячейка на складе или магазине
    ZONE: str = "zone"  # Зона, которая отвечает за агрегацию свойств местоположений, например стратегия приемки или отгрузки
    SCRAP: str = "scrap"  # Класс хранение некондиционного товара


class BlockerEnum(str, Enum):
    """
        **BlockerEnum** - Перечисление, обозначающее различ��ые типы блокировок для местоположений и товаров:
        - FULL_BLOCK: Полная блокировка ячейки и товара в ней для любых действий над ней, например, если происходит инвентаризация.
        - MOVE_BLOCK: Блокировка ячейки для ее перемещения, но может быть, например, пересчитана, или из нее может быть перемещен товар.
        - PRODUCT_BLOCK: Блокировка товара внутри ячейки, например, если он зарезервирован под какие-то движения, но при этом ячейка может быть перемещена.
        - FREE: Значит, что над упаковкой и товар в ней не совершается никаких движений и она свободна.
    """
    FULL_BLOCK: str = "full_block"
    MOVE_BLOCK: str = "move_block"
    PRODUCT_BLOCK: str = "product_block"
    FREE: str = "free"
