import datetime
from typing import Optional, List

from pydantic import BaseModel

from models.cargo import CargoReadModel, CargoModel


class TariffModel(BaseModel):
    date: datetime.date
    rate: float

    cargos: Optional[List[CargoModel]] = None


class TariffUpdateModel(BaseModel):
    date: Optional[datetime.date] = None
    rate: Optional[float] = None


class TariffReadModel(BaseModel):
    id: int

    date: datetime.date
    rate: float

    cargos: List[CargoReadModel]

    class Config:
        from_attributes = True
