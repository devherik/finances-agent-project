import traceback
import asyncio
from sqlalchemy.sql.functions import func
from sqlalchemy.sql._selectable_constructors import select

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.settings import settings
from helpers.loging_helper import logger


async def main():
    """
    Test connection to database. Uses the same pattern as Dependencies.
    """
    logger.info("Initiating connection to database Test.")
    try:
        engine = create_async_engine(settings.get_async_postgres_url)
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(func.now())
            result = await session.execute(query)
            logger.success(f"Current Time: {result.scalar_one()}")
        await engine.dispose()
        logger.info("Connection to database Test closed.")
        logger.spacer()

    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        traceback.print_exc()
        logger.spacer()


if __name__ == "__main__":
    asyncio.run(main())
