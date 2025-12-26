import asyncio
import traceback

from infrastructure.database.models import Base
from helpers.loging_helper import logger
from core.deps import (
    get_postgres_engine,
    get_postgres_async_session,
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
            # 5. Create Vector Repository
            # 6. Embedding
            # 7. Save Interaction
            # 8. Search Similar Interactions
            # 9. Delete Interaction
            # 10. Delete All Interactions

        await engine.dispose()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
