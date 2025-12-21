from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager

from api.routers.auth_routers import auth_r

from helpers.loging_helper import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    yield
    logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan)

app.include_router(auth_r)


@app.get("/")
async def root():
    return {"message": "Hello World"}
