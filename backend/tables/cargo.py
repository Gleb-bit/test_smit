from sqlalchemy import Column, Integer, String, Float

from config.database_conf import Base


class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(String, unique=True, index=True, nullable=False)
    declared_value = Column(Float, nullable=False)
