from pydantic import BaseModel


class CargoModel(BaseModel):
    type: str
    declared_value: float


class CargoReadModel(BaseModel):
    id: int

    type: str
    declared_value: float
