from typing import Annotated, Optional
from fastapi.params import Depends
from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from domain.entities.user_entities import UserBase
from core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def validate_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if username is None:
            return None
        print(username)
        return payload
    except JWTError:
        return None

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserBase:
    """
    Extract and validate user from JWT token.
    Returns a User object if authentication is successful.
    Raises HTTPException if authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = validate_token(token)
    if payload is None:
        raise credentials_exception
    
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
        
    # Create a minimal User object with the username from the token
    # In a real application, you might want to fetch full user details from the database
    user = UserBase(
        username=username,
    )
    
    return user