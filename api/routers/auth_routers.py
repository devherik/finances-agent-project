from aiohttp.web_exceptions import HTTPException
from application.services.auth_service import get_register_user
from domain.entities.user_entities import UserCreate
from application.services.auth_service import get_delete_user
from domain.entities.user_entities import UserUpdate
from application.services.auth_service import get_update_user
from application.services.auth_service import get_hydrate_user, get_logout
from core.deps import AuthUser

from uuid import UUID

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
    if token is None:
        raise HTTPException(reason="Unauthorized")
    return await get_logout(token, user_repo)


@auth_rt.get("/me", response_model=Token)
async def me(
    token: Annotated[str, Depends(oauth2_scheme)],
    user: AuthUser,
):
    if token is None:
        raise HTTPException(reason="Unauthorized")
    return Token(
        access_token=token, token_type="bearer", data={"user": user.model_dump()}
    )


@auth_rt.get("/hydrate", response_model=Token)
async def hydrate(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
):
    if token is None:
        raise HTTPException(reason="Unauthorized")
    return await get_hydrate_user(token, user_repo)


@auth_rt.post("/register", response_model=Token)
async def register(
    token: Annotated[str, Depends(oauth2_scheme)],
    user: UserCreate,
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
):
    if token is None:
        raise HTTPException(reason="Unauthorized")
    return await get_register_user(user, user_repo)


@auth_rt.post("/update", response_model=Token)
async def update(
    token: Annotated[str, Depends(oauth2_scheme)],
    user: UserUpdate,
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
):
    if token is None:
        raise HTTPException(reason="Unauthorized")
    return await get_update_user(user, user_repo)


@auth_rt.post("/delete", response_model=Token)
async def delete(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_id: UUID,
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
):
    if token is None:
        raise HTTPException(reason="Unauthorized")
    return await get_delete_user(user_id, user_repo)
