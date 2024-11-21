from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from config.database_conf import Base
from tables.tariffs import cargo_tariff_association


class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(String, unique=True, index=True, nullable=False)
    declared_value = Column(Float, nullable=False)

    tariffs = relationship(
        "Tariff",
        secondary=cargo_tariff_association,
        back_populates="cargos"
    )
