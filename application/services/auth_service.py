from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from jose.exceptions import JWTError

from core.deps import pwd_context

from domain.entities.user_entities import UserBase
from domain.entities.auth_entities import Token
from domain.repositories import IUserRepository

from helpers.auth_helper import create_access_token, validate_token
from helpers.loging_helper import logger


async def get_login(
    form_data: OAuth2PasswordRequestForm,
    user_repo: IUserRepository,
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


async def get_logout(
    token: str,
    user_repo: IUserRepository,
):
    logger.debug(f"Logout attempt for user: {token}")
    return Token(access_token="", token_type="bearer", data={})


async def get_current_user(
    token: str,
    user_repo: IUserRepository,
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
