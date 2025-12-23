from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from jose.exceptions import JWTError
from typing import Annotated, AsyncGenerator
from passlib.context import CryptContext

from domain.entities.user_entities import UserBase
from domain.repositories import IUserRepository

from infrastructure.database.models import UserModel
from infrastructure.repositories.user_repo import UserRepository

from helpers.auth_helper import validate_token
from helpers.loging_helper import logger

from core.settings import settings

# Dependencies
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/o/token")


def get_postgres_engine() -> AsyncEngine:
    """
    Returns a new postgres engine for the database.
    Always call 'dispose' on the engine when it is no longer needed.
    """
    return create_async_engine(settings.get_async_postgres_url)


async def get_postgres_async_session(
    engine: AsyncEngine = Depends(get_postgres_engine),
) -> AsyncGenerator[AsyncSession, None]:
    """
    Returns a new postgres async session for the database.
    Use with 'async with' statement.
    """
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


def get_user_repository(
    session: AsyncSession = Depends(get_postgres_async_session),
) -> IUserRepository:
    """
    Returns a new instance of the UserRepository injection.
    """
    return UserRepository(UserModel, UserBase, session)


# TODO: Create here the dependencies for the other repositories


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: IUserRepository = Depends(get_user_repository),
) -> UserBase:
    """
    Returns the current user.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = validate_token(token)
        if payload is None:
            raise credentials_exception

        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        email: str = sub
    except JWTError:
        raise credentials_exception

    try:
        user = await user_repo.get_by_email(email)
        if user is None:
            raise credentials_exception
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return user


# Dependencies Injection
PostgresEngine = Depends(get_postgres_engine)
PostgresAsyncSession = Depends(get_postgres_async_session)
UserRepo = Depends(get_user_repository)
CurrentUser = Depends(get_current_user)


# Types
AuthUser = Annotated[UserBase, Depends(get_current_user)]
