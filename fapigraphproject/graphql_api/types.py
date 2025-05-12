from datetime import datetime
from typing import List, Optional

import strawberry
import strawberry.types


@strawberry.type
class UserOther:
    id: int
    username: str


@strawberry.type
class Chat:
    id: int
    name: Optional[str]
    is_group: bool
    chatmembers: List[UserOther]


@strawberry.input
class ChatCreationData:
    name: str
    member_ids: List[int]


@strawberry.type
class UserSelf:
    id: int
    username: str
    chats: List[Chat]


@strawberry.type
class Token:
    value: str
    token_type: str


@strawberry.type
class LoginSuccess:
    access_token: str
    refresh_token: str
    token_type: str


@strawberry.type
class Success:
    message: str


@strawberry.type
class Message:
    id: int
    sender_id: int
    content: str
    sent_at: datetime


@strawberry.type
class ChatDetails:
    id: int
    name: Optional[str]
    messages: List[Message]
    members: List[UserOther]
    is_group: bool


@strawberry.input
class LoginInput:
    username: str
    password: str
