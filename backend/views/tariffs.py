from datetime import datetime, date

from fastapi import APIRouter, HTTPException
from fastapi.params import Query, Depends
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from auth.conf import AUTH_MODEL, auth
from config.database_conf import get_session
from config.kafka_producer import KafkaProducer
from config.settings import KAFKA_BROKER_URL, KAFKA_TOPIC
from core.sqlalchemy.crud import Crud
from core.sqlalchemy.orm import Orm
from models.tariffs import TariffModel, TariffReadModel, TariffUpdateModel
from tables.cargo import Cargo
from tables.tariffs import Tariff

tariffs_router = APIRouter()
crud = Crud(Tariff)

producer = KafkaProducer(KAFKA_BROKER_URL, KAFKA_TOPIC)


@tariffs_router.get("/get_tariff_rate/")
async def get_tariff_rate(
    date: date = Query(description="Дата"),
    cargo_type: str = Query(description="Тип груза"),
    session: AsyncSession = Depends(get_session),
):
    tariff_filter = and_(Tariff.date == date, Cargo.type == cargo_type)
    tariff = await Orm.scalar(Tariff, session, tariff_filter, Tariff.cargos, True)

    if not tariff:
        raise HTTPException(400, "Для данной даты/названия грузов не найдено")

    return {"rate": tariff.rate}


@tariffs_router.get("/", response_model=list[TariffReadModel])
async def list_tariffs(session: AsyncSession = Depends(get_session)):
    return await crud.list(session, Tariff.cargos)


@tariffs_router.get("/{tariff_id}/", response_model=TariffReadModel)
async def retrieve_tariff(tariff_id: int, session: AsyncSession = Depends(get_session)):
    return await crud.retrieve(tariff_id, session)


@tariffs_router.post("/", response_model=TariffReadModel)
async def create_tariff(
    data: TariffModel,
    session: AsyncSession = Depends(get_session),
    credentials: AUTH_MODEL = Depends(auth.get_request_user),
):
    instance = await crud.create(data, session, Tariff.cargos)

    producer.send_message(
        {
            "user_id": credentials.email,
            "action": "CREATE_TARIFF",
            "timestamp": datetime.now().isoformat(),
        }
    )

    return instance


@tariffs_router.patch("/{tariff_id}/", response_model=TariffReadModel)
async def update_tariff(
    tariff_id: int,
    data: TariffUpdateModel,
    session: AsyncSession = Depends(get_session),
    credentials: AUTH_MODEL = Depends(auth.get_request_user),
):
    instance = await crud.update(
        data.model_dump(exclude_unset=True), tariff_id, session, Tariff.cargos
    )

    producer.send_message(
        {
            "user_id": credentials.email,
            "action": "UPDATED_TARIFF",
            "timestamp": datetime.now().isoformat(),
        }
    )

    return instance


@tariffs_router.delete("/{tariff_id}/")
async def delete_tariff(
    tariff_id: int,
    session: AsyncSession = Depends(get_session),
    credentials: AUTH_MODEL = Depends(auth.get_request_user),
):
    producer.send_message(
        {
            "user_id": credentials.email,
            "action": "UPDATED_TARIFF",
            "timestamp": datetime.now().isoformat(),
        }
    )

    return await crud.delete(tariff_id, session)
