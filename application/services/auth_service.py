from core.deps import pwd_context
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from helpers.auth_helper import create_access_token
from jose.exceptions import JWTError
from helpers.auth_helper import validate_token
from fastapi import Depends
from fastapi.exceptions import HTTPException

from typing import Annotated

from domain.entities.user_entities import UserBase
from domain.entities.auth_entities import Token
from domain.repositories import IUserRepository

from helpers.loging_helper import logger

from core.deps import get_user_repository, oauth2_scheme


async def get_login(
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


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: IUserRepository = Depends(get_user_repository),
) -> UserBase:
    """
    Returns the current user.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = validate_token(token)
        if payload is None:
            raise credentials_exception

        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        email: str = sub
    except JWTError:
        raise credentials_exception

    try:
        user = await user_repo.get_by_email(email)
        if user is None:
            raise credentials_exception
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    return user
