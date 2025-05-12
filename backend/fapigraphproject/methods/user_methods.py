from sqlmodel import Sequence, Session, col, select

from fapigraphproject.models import AppUser


def get_users_by_name(lookup: str, session: Session) -> Sequence[AppUser]:
    return session.exec(
        select(AppUser).where(col(AppUser.username).regexp_match(lookup, "i"))
    ).all()
