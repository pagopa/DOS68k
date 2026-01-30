from functools import lru_cache
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from .env import get_db_settings, DBSettings

@lru_cache()
def get_async_engine() -> AsyncEngine:
    db_settings: DBSettings = get_db_settings()

    db_url: URL = URL.create(
        drivername="postgresql+asyncpg",
        username=db_settings.DB_USERNAME,
        password=db_settings.DB_PASSWORD.get_secret_value(),
        port=db_settings.DB_PORT,
        database=db_settings.DB_NAME,
        host=db_settings.DB_HOST,
    )

    return create_async_engine(url=db_url)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    engine: AsyncEngine = get_async_engine()
    async_session: sessionmaker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
