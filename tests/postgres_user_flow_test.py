from domain.repositories import IUserRepository
import traceback
import asyncio

from helpers.loging_helper import logger
from infrastructure.database.models import Base
from helpers.auth_helper import get_password_hash, verify_password
from domain.entities.user_entities import UserCreate, UserUpdate
from core.deps import (
    get_postgres_engine,
    get_postgres_async_session,
    get_user_repository,
)


async def main():
    try:
        # 1. Create Async Engine
        # We need an async driver (asyncpg) which we added to settings
        engine = get_postgres_engine()

        # 2. Create Tables (if not exist)
        # In production, use Alembic. For playground, this is fine.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 3. Create Session Factory
        AsyncSessionLocal = await get_postgres_async_session(engine)

        # 4. Use Session
        async with AsyncSessionLocal() as session:
            user_repository: IUserRepository = get_user_repository(session)

            logger.info("Hashing and verifying password...")
            password = "strongpassword123"
            hashed_password = get_password_hash(password)
            assert verify_password(password, hashed_password)
            logger.success("Password hashed and verified successfully.")

            logger.info("Creating user...")
            new_user = await user_repository.create(
                UserCreate(
                    name="New User",
                    email="newuser@mail.com",
                    password=hashed_password,
                    cpf="12345678901",
                    cnpj="12345678901234",
                    phone="12345678901",
                )
            )
            logger.success(f"Created User: {new_user}")
            logger.spacer()

            logger.info("Fetching user...")
            fetched_user = await user_repository.get(new_user.id)
            logger.success(f"Fetched User: {fetched_user}")
            logger.spacer()

            logger.info("Updating user...")
            updated_user = await user_repository.update(
                new_user.id,
                UserUpdate(
                    name="Updated User",
                    email="updateduser@mail.com",
                    cnpj="12345678901234",
                    phone="12345678901",
                ),
            )
            logger.success(f"Updated User: {updated_user}")
            logger.spacer()

            logger.info("Verifying updated password...")
            assert verify_password(password, updated_user.password)
            logger.success("Updated password verified successfully.")
            logger.spacer()

            logger.info("Deleting user...")
            await user_repository.delete(new_user.id)
            logger.success("User deleted")
            logger.spacer()

    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
