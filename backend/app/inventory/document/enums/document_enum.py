from enum import Enum


class DocumentClass(str, Enum):
    DIRECT_DELIVERY:        str = 'Direct Delivery'    # Прямая отгрузка контрагенту (клиенту например)
    INBOUND_DELIVERY:       str = 'Inbound Delivery'   # Входящая поставка
    OUTBOUND_DELIVERY:      str = 'Outbound Delivery'  # Исходящая поставка
    SCRAP:                  str = 'Scrap'              # Списание
    INVENTORY:              str = 'Inventory'          # Инвентаризация
    TRANSFER:               str = 'Transfer'           # Перемещение склад-склад
    BILD:                   str = 'Bild'               # Производство


