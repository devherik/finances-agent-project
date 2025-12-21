from core.deps import get_postgres_async_session
from google.genai.live import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from core.deps import get_current_user
from core.deps import oauth2_scheme
from core.deps import pwd_context
from core.deps import get_user_repository

from domain.entities.auth_entities import Token
from domain.repositories import IUserRepository
from helpers.auth_helper import create_access_token
from helpers.loging_helper import logger

auth_rt = APIRouter(prefix="/o", tags=["Authentication"])


@auth_rt.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    AsyncSession: Annotated[AsyncSession, Depends(get_postgres_async_session)],
):
    logger.debug(f"Login attempt for user: {form_data.username}")

    async with AsyncSession() as session:
        user_repo = get_user_repository(session)
        user = await user_repo.get_by_email(form_data.username)

    if user is None:
        logger.debug("User not found")
        raise HTTPException(status_code=400, detail="User not found")
    if not pwd_context.verify(form_data.password, user.password):
        logger.debug("Incorrect password")
        raise HTTPException(status_code=400, detail="Incorrect password")
    access_token = create_access_token(data={"sub": user.email})
    logger.debug("Login successful")
    return Token(access_token=access_token, token_type="bearer", data={})


@auth_rt.get("/me", response_model=Token)
async def me(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: IUserRepository = Depends(get_user_repository),
):
    return await get_current_user(token, user_repo)


@auth_rt.post("/register", response_model=Token)
async def register():
    return Token(access_token="", token_type="bearer", data={})
