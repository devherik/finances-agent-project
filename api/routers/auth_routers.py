from core.deps import AuthUser

from fastapi import APIRouter, HTTPException, Depends
from domain.repositories import IUserRepository
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from core.deps import oauth2_scheme
from core.deps import pwd_context
from core.deps import get_user_repository

from domain.entities.auth_entities import Token
from helpers.auth_helper import create_access_token
from helpers.loging_helper import logger

auth_rt = APIRouter(prefix="/o", tags=["Authentication"])


@auth_rt.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
):
    logger.debug(f"Login attempt for user: {form_data.username}")

    try:
        user = await user_repo.get_by_email(form_data.username)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
    user: AuthUser,
):
    return Token(
        access_token=token, token_type="bearer", data={"user": user.model_dump()}
    )


@auth_rt.post("/register", response_model=Token)
async def register():
    return Token(access_token="", token_type="bearer", data={})
