from enum import Enum


class StaffPosition(str, Enum):
    """
    - Кладовщик
    - Старший кладовщик
    - Замиститель директора магазина
    - Директор магазина
    - Супервайзер
    """
    STOREKEEPER: str = "storekeeper"
    SENIOR_STOREKEEPER: str = "senior_storekeeper"
    DEPUTY_STORE_MANAGER: str = "deputy_store_manager"
    STORE_MANAGER: str = "store_manager"
    SUPERVISOR: str = "supervisor"


