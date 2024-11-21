import datetime

from fastapi import APIRouter, HTTPException
from fastapi.params import Query, Depends
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from config.database_conf import get_session
from core.sqlalchemy.crud import Crud
from core.sqlalchemy.orm import Orm
from models.tariffs import TariffModel, TariffReadModel, TariffUpdateModel
from tables.cargo import Cargo
from tables.tariffs import Tariff

tariffs_router = APIRouter()
crud = Crud(Tariff)


@tariffs_router.get("/get_tariff_rate/")
async def get_tariff_rate(
    date: datetime.date = Query(description="Дата"),
    cargo_type: str = Query(description="Тип груза"),
    session: AsyncSession = Depends(get_session),
):
    tariff_filter = and_(Tariff.date == date, Cargo.type == cargo_type)
    tariff = await Orm.scalar(Tariff, session, tariff_filter, Tariff.cargos)

    if not tariff:
        raise HTTPException(400, "Для данной даты грузов не найдено")

    return {"rate": tariff.rate}


@tariffs_router.get("/", response_model=list[TariffReadModel])
async def list_tariffs(session: AsyncSession = Depends(get_session)):
    return await crud.list(session, Tariff.cargos)


@tariffs_router.get("/{tariff_id}/", response_model=TariffReadModel)
async def retrieve_tariff(
    tariff_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await crud.retrieve(tariff_id, session)


@tariffs_router.post("/", response_model=TariffReadModel)
async def create_tariff(
    data: TariffModel,
    session: AsyncSession = Depends(get_session),
):
    instance = await crud.create(data, session, Tariff.cargos)

    return instance


@tariffs_router.patch("/{tariff_id}/", response_model=TariffReadModel)
async def update_tariff(
    tariff_id: int,
    data: TariffUpdateModel,
    session: AsyncSession = Depends(get_session),
):
    return await crud.update(data.model_dump(exclude_unset=True), tariff_id, session)


@tariffs_router.delete("/{tariff_id}/")
async def delete_tariff(
    tariff_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await crud.delete(tariff_id, session)
