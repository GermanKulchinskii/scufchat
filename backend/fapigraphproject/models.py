from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, func


class ChatMember(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id")
    user_id: int = Field(foreign_key="appuser.id")
    joined_at: datetime = Field(default_factory=lambda: func.now(), nullable=False)


class AppUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    created_at: datetime = Field(default_factory=lambda: func.now(), nullable=False)
    chats: List["Chat"] = Relationship(
        back_populates="chatmembers", link_model=ChatMember
    )


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_group: bool
    name: Optional[str]
    messages: List["Message"] = Relationship(back_populates="chat")
    chatmembers: List[AppUser] = Relationship(
        back_populates="chats", link_model=ChatMember
    )
    owner_id: int = Field(foreign_key="appuser.id")


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: int = Field(foreign_key="appuser.id")
    content: str
    sent_at: datetime = Field(default_factory=lambda: func.now(), nullable=False)
    chat: Optional[Chat] = Relationship(back_populates="messages")
