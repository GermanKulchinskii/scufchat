import strawberry
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from fapigraphproject.methods.chat_methods import (
    check_user_in_chat,
    get_chat_by_id,
    get_user_chats,
)
from fapigraphproject.methods.user_methods import get_users_by_name

from ..methods.authentication_methods import authenticate_by_token
from .types import ChatDetails, UserOther, UserSelf


@strawberry.type
class Query:

    @strawberry.field
    def current(self, info: strawberry.Info) -> UserSelf:
        session = info.context["session"]
        current_user = authenticate_by_token(info, session)
        chats = get_user_chats(current_user.id, session)
        return UserSelf(id=current_user.id, username=current_user.username, chats=chats)

    @strawberry.field
    def find_users(self, info: strawberry.Info, username: str) -> list[UserOther]:
        if len(username) <= 1:
            return []
        session = info.context["session"]
        current_user = authenticate_by_token(info, session)
        matches = get_users_by_name(username, session)
        matches = [user for user in matches if user.id != current_user.id]
        return matches

    @strawberry.field
    def get_chat(
        self, info: strawberry.Info, chat_id: int, offset: int = 0, limit: int = 10
    ) -> ChatDetails:
        session = info.context["session"]
        user = authenticate_by_token(info, session)
        try:
            check_user_in_chat(chat_id, user.id, session)
        except NoResultFound:
            raise HTTPException(403, detail="You can't access this chat.")
        chat = get_chat_by_id(chat_id, session)
        chat_messages = sorted(chat.messages, key=lambda x: x.sent_at, reverse=True)
        paginated_messages = chat_messages[offset : offset + limit]
        return ChatDetails(
            id=chat.id,
            name=chat.name,
            messages=paginated_messages,
            members=[
                UserOther(id=member.id, username=member.username)
                for member in chat.chatmembers
            ],
            is_group=chat.is_group,
        )
