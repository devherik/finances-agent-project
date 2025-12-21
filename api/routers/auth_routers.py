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

auth_r = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_r.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: IUserRepository = Depends(get_user_repository),
):
    logger.info(f"Login attempt for user: {form_data.username}")
    user = await user_repo.get_by_email(form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer", data={})


@auth_r.get("/me", response_model=Token)
async def me(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: IUserRepository = Depends(get_user_repository),
):
    return await get_current_user(token, user_repo)


@auth_r.post("/register", response_model=Token)
async def register():
    return Token(access_token="", token_type="bearer", data={})
