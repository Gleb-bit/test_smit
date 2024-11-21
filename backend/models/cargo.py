from pydantic import BaseModel


class CargoModel(BaseModel):
    type: str
    declared_value: float

    class Config:
        from_attributes = True


class CargoReadModel(BaseModel):
    id: int

    type: str
    declared_value: float

    class Config:
        from_attributes = True
