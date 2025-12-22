from application.services.auth_service import get_logout
from core.deps import AuthUser

from fastapi import APIRouter, Depends
from domain.repositories import IUserRepository
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from application.services.auth_service import get_login

from core.deps import oauth2_scheme
from core.deps import get_user_repository

from domain.entities.auth_entities import Token

auth_rt = APIRouter(prefix="/o", tags=["Authentication"])


@auth_rt.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
):
    return await get_login(form_data, user_repo)


@auth_rt.post("/logout", response_model=Token)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
):
    return await get_logout(token, user_repo)


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
