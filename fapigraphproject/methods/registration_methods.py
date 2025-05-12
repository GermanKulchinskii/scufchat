from fastapi import HTTPException
from sqlmodel import Session, select

from fapigraphproject.models import AppUser

from .authentication_methods import get_password_hash


def register_user(username: str, password: str, session: Session) -> AppUser:
    existing_user = session.exec(
        select(AppUser).where(AppUser.username == username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already present")
    hashed_pw = get_password_hash(password)
    user = AppUser(username=username, password=hashed_pw)
    session.add(user)
    session.commit()
    return session.exec(select(AppUser).where(AppUser.username == username)).one()
