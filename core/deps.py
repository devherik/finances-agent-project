from fastapi import Depends

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from domain.entities.user_entities import UserBase
from domain.repositories import IUserRepository
from infrastructure.database.models import UserModel
from infrastructure.repositories.user_repo import UserRepository

from core.settings import settings


def get_postgres_engine() -> AsyncEngine:
    """
    Returns a new postgres engine for the database.
    Always call 'dispose' on the engine when it is no longer needed.
    """
    return create_async_engine(settings.get_async_postgres_url)


async def get_postgres_async_session(
    engine: AsyncEngine = Depends(get_postgres_engine),
) -> AsyncSession:
    """
    Returns a new postgres async session for the database.
    Use with 'async with' statement.
    """
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    return async_session


def get_user_repository(
    session: AsyncSession = Depends(get_postgres_async_session),
) -> IUserRepository:
    """
    Returns a new instance of the UserRepository injection.
    """
    return UserRepository(UserModel, UserBase, session)


PostgresEngine = Depends(get_postgres_engine)
PostgresAsyncSession = Depends(get_postgres_async_session)
UserRepo = Depends(get_user_repository)
