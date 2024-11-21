from fastapi import APIRouter, HTTPException
from fastapi.params import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.conf import AUTH_MODEL, auth
from config.database_conf import get_session
from config.settings import MAIN_URL
from core.httpx.request import send_request
from core.sqlalchemy.orm import Orm
from tables.cargo import Cargo

insurance_router = APIRouter()


@insurance_router.get("/get_insurance/")
async def get_insurance(
    date: str = Query(description="Дата"),
    cargo_type: str = Query(description="Тип груза"),
    session: AsyncSession = Depends(get_session),
    credentials: AUTH_MODEL = Depends(auth.get_request_user),
):
    cargo = await Orm.scalar(Cargo, session, Cargo.type == cargo_type)
    if not cargo:
        raise HTTPException(400, "Указанного груза нет в базе данных")

    response, status_code = await send_request(
        f"{MAIN_URL}/rates/get_tariff_rate/",
        params={"date": date, "cargo_type": cargo_type},
    )
    if status_code != 200:
        return response

    return {
        "Стоимость страхования": round(
            cargo.declared_value * float(response["rate"]), 2
        )
    }
