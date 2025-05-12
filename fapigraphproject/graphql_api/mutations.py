from datetime import timedelta

import strawberry
from fastapi import HTTPException, status

from fapigraphproject.methods.chat_methods import (
    create_group_chat,
    create_private_chat,
    delete_chat,
    transfer_chat_ownership,
    update_chat_user_list,
)
from fapigraphproject.methods.registration_methods import register_user

from ..config import Config
from ..methods.authentication_methods import (
    authenticate_by_token,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from .types import (
    ChatCreationData,
    ChatDetails,
    LoginInput,
    LoginSuccess,
    Token,
    UserOther,
)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, info: strawberry.Info, input: LoginInput) -> LoginSuccess:
        session = info.context["session"]
        user = register_user(input.username, input.password, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRES_MINUTES)
        refresh_token_expires = timedelta(days=Config.REFRESH_TOKEN_EXPIRES_DAYS)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username}, expires_delta=refresh_token_expires
        )
        return LoginSuccess(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @strawberry.mutation
    def login(self, info: strawberry.Info, input: LoginInput) -> LoginSuccess:
        session = info.context["session"]
        user = authenticate_user(input.username, input.password, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRES_MINUTES)
        refresh_token_expires = timedelta(days=Config.REFRESH_TOKEN_EXPIRES_DAYS)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username}, expires_delta=refresh_token_expires
        )
        return LoginSuccess(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    @strawberry.mutation
    def refresh_access_token(self, info: strawberry.Info, refresh_token: str) -> Token:
        session = info.context["session"]
        user = get_current_user(refresh_token, session)
        access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRES_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(value=access_token, token_type="bearer")

    @strawberry.mutation
    def start_group_chat(
        self, info: strawberry.Info, creation_data: ChatCreationData
    ) -> ChatDetails:
        session = info.context["session"]
        user = authenticate_by_token(info, session)
        group_chat = create_group_chat(
            user, creation_data.name, creation_data.member_ids, session
        )
        return ChatDetails(
            id=group_chat.id,
            name=group_chat.name,
            messages=group_chat.messages,
            members=[
                UserOther(id=member.id, username=member.username)
                for member in group_chat.members
            ],
            is_group=True,
        )

    @strawberry.mutation
    def start_or_get_private_chat(
        self, info: strawberry.Info, second_user_id: int
    ) -> ChatDetails:
        session = info.context["session"]
        user = authenticate_by_token(info, session)
        private_chat = create_private_chat(user.id, second_user_id, session)
        return ChatDetails(
            id=private_chat.id,
            name=private_chat.name,
            messages=sorted(
                private_chat.messages, key=lambda x: x.sent_at, reverse=True
            ),
            members=[
                UserOther(id=member.id, username=member.username)
                for member in private_chat.members
            ],
            is_group=False,
        )

    @strawberry.mutation
    def delete_chat(self, info: strawberry.Info, chat_id: int) -> None:
        session = info.context["session"]
        user = authenticate_by_token(info, session)
        delete_chat(user.id, chat_id, session)
        return None

    @strawberry.mutation
    def alter_chat_user_list(
        self, info: strawberry.Info, chat_id: int, user_id: int, is_to_add: bool
    ) -> None:
        session = info.context["session"]
        user = authenticate_by_token(info, session)
        update_chat_user_list(user.id, chat_id, user_id, is_to_add, session)

    @strawberry.mutation
    def transfer_chat_ownership(
        self, info: strawberry.Info, chat_id: int, new_owner_id: int
    ) -> None:
        session = info.context["session"]
        user = authenticate_by_token(info, session)
        transfer_chat_ownership(user.id, chat_id, new_owner_id, session)
