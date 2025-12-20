from core.deps import get_postgres_async_session
import asyncio


from domain.repositories import IUserRepository
from domain.entities.user_entities import UserBase, UserCreate, UserUpdate
from infrastructure.repositories.user_repo import UserRepository
from infrastructure.database.models import Base, UserModel
from helpers.auth_helper import get_password_hash, verify_password
from helpers.loging_helper import logger
from core.deps import get_postgres_engine


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
        AsyncSessionLocal = get_postgres_async_session(engine)

        # 4. Use Session
        async with AsyncSessionLocal() as session:
            # Instantiate Repository with ORM Model AND Domain Model
            user_repository: IUserRepository = UserRepository(
                UserModel, UserBase, session
            )

            logger.info("Hashing and verifying password...")
            password = "strongpassword123"
            hashed_password = get_password_hash(password)
            assert verify_password(password, hashed_password)
            logger.success("Password hashed and verified successfully.")

            logger.info("Creating user...")
            new_user = await user_repository.create(
                UserCreate(
                    name="Herik Rezende",
                    email="herikrezende@gmail.com",
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
                    name="Herik R. Updated",
                    email="herikupdated@gmail.com",
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

        await engine.dispose()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
