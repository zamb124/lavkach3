import uuid
from enum import Enum
from typing import Optional

from sqlalchemy import Sequence, Uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped

from core.db import Base
from core.db.mixins import AllMixin, CreatedEdited


class IdentificationType(str, Enum):
    PASSPORT:   str = 'passport'
    IQAMA:      str = 'iqama'


class Prescription(Base, AllMixin, CreatedEdited):
    """
         Рецепт, который выписывает врач пациенту
         заполняет:
          - Сам препарат, его количество и дозировку
    """
    __tablename__ = "prescription"
    lsn_seq = Sequence(f'prescription_lsn_seq')
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    #title: Mapped[str] = mapped_column(index=True)
    #external_number: Mapped[Optional[str]] = mapped_column(unique=True)
    number: Mapped[str] = mapped_column(index=True)  # Человекочитаемый номер присвается по формуле - {ГОД(2)}-{МЕСЯЦ}-{ДЕНЬ}-{LSN}
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True, nullable=True) # препарат
    identification_type: Mapped[str]
    patient_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, index=True) # пациент (тоже пользователь)


