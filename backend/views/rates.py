import json

from fastapi import APIRouter, HTTPException
from fastapi.params import Query

rates_router = APIRouter()


def load_rates_from_file(file_path: str):
    with open(file_path, "r") as file:
        return json.load(file)


@rates_router.get("/get_tariff_rate/")
async def get_tariff_rate(
    date: str = Query(description="Дата"),
    cargo_type: str = Query(description="Тип груза"),
):
    rates = load_rates_from_file("rates.json")
    cargos = rates.get(date)

    if not cargos:
        raise HTTPException(400, "Для данной даты грузов не найдено")

    for rate in cargos:
        if rate["cargo_type"] == cargo_type:
            return {"rate": rate["rate"]}

    raise HTTPException(400, "Для данного типа груза тарифов не найдено")
