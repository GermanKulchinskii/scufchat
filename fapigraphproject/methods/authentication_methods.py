from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
import strawberry
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select

from fapigraphproject.config import Config
from fapigraphproject.models import AppUser

pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

secret_key = Config.JWT_SECRET

hash_algorithm = Config.JWT_ALGORITHM


class TokenData(BaseModel):
    username: str | None = None


def verify_password(plain_password: str, hashed_password: str):
    return pw_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pw_context.hash(password)


def get_user(username: str, session: Session):
    result = session.exec(select(AppUser).where(AppUser.username == username)).one()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


def get_user_by_id(user_id: int, session):
    result = session.exec(select(AppUser).where(AppUser.id == user_id)).one()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


def authenticate_user(username: str, password: str, session: Session) -> AppUser | None:
    user = get_user(username, session)
    if user and verify_password(password, user.password):
        return user
    return None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"iat": datetime.now(timezone.utc)})
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=hash_algorithm)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"iat": datetime.now(timezone.utc)})
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=hash_algorithm)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[hash_algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user


def authenticate_by_token(info: strawberry.Info, session: Session) -> AppUser:
    auth_header = info.context["request"].headers.get("Authorization")
    access_token = auth_header.split(" ")[1] if auth_header else None
    current_user = get_current_user(access_token, session)
    return current_user
