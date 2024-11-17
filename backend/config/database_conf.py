from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import DATABASE_URL

Base = declarative_base()

engine = create_async_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, future=True)


async def get_session():
    async with SessionLocal() as session:
        yield session
