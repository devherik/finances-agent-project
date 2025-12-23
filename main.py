from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine

from api.routers.auth_routers import auth_rt

from helpers.loging_helper import logger
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create singleton database engine
    logger.info("Starting application...")
    logger.info("Creating database engine...")

    engine = create_async_engine(
        settings.get_async_postgres_url,
        echo=False,  # Set to True for SQL query logging
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,  # Number of connections to maintain
        max_overflow=10,  # Additional connections when pool is exhausted
    )

    app.state.engine = engine
    logger.info("Database engine created successfully")

    yield

    # Shutdown: Dispose engine and close all connections
    logger.info("Shutting down application...")
    logger.info("Disposing database engine...")
    await app.state.engine.dispose()
    logger.info("Database engine disposed successfully")


app = FastAPI(lifespan=lifespan)

app.include_router(auth_rt)


@app.get("/")
async def root():
    return {"message": "Hello World"}
