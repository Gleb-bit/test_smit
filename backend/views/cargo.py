from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.conf import AUTH_MODEL, auth
from config.database_conf import get_session
from core.sqlalchemy.crud import Crud
from models.cargo import CargoModel, CargoReadModel
from tables.cargo import Cargo

cargo_router = APIRouter()
crud = Crud(Cargo)


@cargo_router.post("/create/", response_model=CargoReadModel)
async def create_cargo(
    data: CargoModel,
    session: AsyncSession = Depends(get_session),
    credentials: AUTH_MODEL = Depends(auth.get_request_user),
):
    return await crud.create(data, session)
