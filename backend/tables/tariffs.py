from sqlalchemy import (
    Column,
    Integer,
    Date,
    Float,
    ForeignKey,
    Table,
    UniqueConstraint,
    String,
)
from sqlalchemy.orm import relationship

from config.database_conf import Base

cargo_tariff_association = Table(
    "cargo_tariff",
    Base.metadata,
    Column("cargo_id", Integer, ForeignKey("cargos.id"), primary_key=True),
    Column("tariff_id", Integer, ForeignKey("tariffs.id"), primary_key=True),
    UniqueConstraint("cargo_id", "tariff_id", name="unique_cargo_tariff"),
)


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True)

    date = Column(Date, unique=True, nullable=False)
    rate = Column(Float, nullable=False)

    cargos = relationship(
        "Cargo",
        secondary=cargo_tariff_association,
        back_populates="tariffs"
    )
