from fastapi import Depends
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.settings import settings


def get_postgres_engine() -> AsyncEngine:
    """
    Returns a new postgres engine for the database.
    Always call 'dispose' on the engine when it is no longer needed.
    """
    return create_async_engine(settings.get_async_postgres_url)


def get_postgres_async_session(
    engine: AsyncEngine = Depends(get_postgres_engine),
) -> AsyncSession:
    """
    Returns a new postgres async session for the database.
    Use with 'async with' statement.
    """
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    return async_session


PostgresEngine = Depends(get_postgres_engine)
PostgresAsyncSession = Depends(get_postgres_async_session)
