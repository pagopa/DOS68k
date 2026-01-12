from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

from .env import db_settings

db_url: URL = URL.create(
    drivername="postgresql+asyncpg",
    username=db_settings.DB_USERNAME,
    password=db_settings.DB_PASSWORD.get_secret_value(),
    port=db_settings.DB_PORT,
    database=db_settings.DB_NAME,
    host=db_settings.DB_HOST,
)
engine: AsyncEngine = create_async_engine(url=db_url)
async_session: sessionmaker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def populate_db() -> None:
    """Create all db tables, based on SQLAlchemy models
    """
    # if ENV == "staging": # For dev/prod we use alembic migrations
    #     async with engine.begin() as conn:
    #         await conn.run_sync(fn=Base.metadata.create_all)
    ...

async def get_db_session():
    """Get db session. Can be used both as FastAPI dependency and as async context manager.

    Yields:
        AsyncSession: db async session
    """
    async with async_session() as session:
        yield session