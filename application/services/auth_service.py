from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from uuid import UUID
from jose.exceptions import JWTError

from domain.entities.user_entities import UserBase, UserUpdate, UserCreate
from domain.entities.auth_entities import Token
from domain.repositories import IUserRepository

from helpers.auth_helper import (
    create_access_token,
    validate_token,
    verify_password,
    get_password_hash,
)
from helpers.loging_helper import logger


async def get_login(
    form_data: OAuth2PasswordRequestForm,
    user_repo: IUserRepository,
):
    logger.debug(
        f"Login attempt for user: {form_data.username}",
    )

    try:
        user = await user_repo.get_by_email(form_data.username)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if user is None:
        logger.debug("User not found")
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(form_data.password, user.password):
        logger.debug("Incorrect password")
        raise HTTPException(status_code=400, detail="Incorrect password")
    access_token = create_access_token(data={"sub": user.email})
    logger.debug("Login successful")
    return Token(
        access_token=access_token, token_type="bearer", data={"user": user.model_dump()}
    )


async def get_logout(
    token: str,
    user_repo: IUserRepository,
):
    logger.debug(f"Logout attempt for user: {token}")
    return Token(access_token="", token_type="bearer", data={})


async def get_hydrate_user(
    token: str,
    user_repo: IUserRepository,
):
    user = await get_current_user(token, user_repo)
    return Token(
        access_token=token, token_type="bearer", data={"user": user.model_dump()}
    )


async def get_register_user(
    user: UserCreate,
    user_repo: IUserRepository,
):
    logger.debug(f"Register attempt for user: {user.email}")
    try:
        existing_user = await user_repo.get_by_email(user.email)
    except Exception as e:
        logger.error(f"An error occurred while checking for existing user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user.password = get_password_hash(user.password)

    try:
        new_user = await user_repo.create(user)
    except Exception as e:
        logger.error(f"An error occurred creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    access_token = create_access_token(data={"sub": new_user.email})
    return Token(
        access_token=access_token,
        token_type="bearer",
        data={"user": new_user.model_dump()},
    )


async def get_update_user(
    token: str,
    user: UserUpdate,
    user_repo: IUserRepository,
):
    current_user = await get_current_user(token, user_repo)
    logger.debug(f"Update attempt for user: {current_user.email}")
    try:
        updated_user = await user_repo.update(current_user.id, user)
    except Exception as e:
        logger.error(f"An error occurred updating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if updated_user is None:
        raise HTTPException(status_code=400, detail="Could not update user")

    return Token(
        access_token=token,
        token_type="bearer",
        data={"user": updated_user.model_dump()},
    )


async def get_delete_user(
    token: str,
    user_id: UUID,
    user_repo: IUserRepository,
):
    current_user = await get_current_user(token, user_repo)
    logger.debug(f"Delete attempt for user: {current_user.id}")

    # Optional: Verify if the user being deleted is the current user or check admin rights
    # For now, let's assume a user can only delete themselves if user_id matches
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this user"
        )

    try:
        await user_repo.delete(user_id)
    except Exception as e:
        logger.error(f"An error occurred deleting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
