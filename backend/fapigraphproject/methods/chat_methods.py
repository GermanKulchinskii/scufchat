from typing import List, Optional

from sqlmodel import Session, select

from fapigraphproject.errors import ChatWithSelfError, InvalidUserIdError
from fapigraphproject.methods.authentication_methods import get_user_by_id
from fapigraphproject.models import AppUser, Chat, ChatMember


def create_chat(
    is_group: bool,
    chat_name: Optional[str],
    member_ids: List[int],
    session: Session,
    owner_id: int,
):
    chat = Chat(is_group=is_group, name=chat_name, owner_id=owner_id)
    statement = select(AppUser).where(AppUser.id.in_(member_ids))
    results = session.exec(statement).all()
    existing_user_ids = {user.id for user in results}
    if not set(member_ids).issubset(existing_user_ids):
        raise InvalidUserIdError()
    session.add(chat)
    session.flush()
    chat_members = [ChatMember(chat_id=chat.id, user_id=id) for id in member_ids]
    session.add_all(chat_members)
    session.commit()
    return chat


def find_private_chat(user1: AppUser, user2: AppUser, session: Session) -> Chat:
    user1_chats = select(ChatMember.chat_id).where(ChatMember.user_id == user1.id)
    user2_chats = select(ChatMember.chat_id).where(ChatMember.user_id == user2.id)

    common_chats = (
        select(Chat.id).where(Chat.id.in_(user1_chats)).where(Chat.id.in_(user2_chats))
    )

    query = (
        select(Chat).where(Chat.is_group.is_(False)).where(Chat.id.in_(common_chats))
    )

    result = session.exec(query).first()
    return result


def create_private_chat(user_id: int, second_user_id: int, session: Session) -> Chat:
    if user_id == second_user_id:
        raise ChatWithSelfError()
    user = get_user_by_id(user_id, session)
    second_user = get_user_by_id(second_user_id, session)
    found_private = find_private_chat(user, second_user, session)
    if found_private:
        return found_private
    return create_chat(
        False,
        f"Чат между {user.username} и {second_user.username}",
        [user.id, second_user.id],
        session,
        user_id,
    )


def create_group_chat(
    user: AppUser, chat_name: str, member_ids: List[int], session: Session
):
    member_ids.append(user.id)
    member_ids = list(set(member_ids))
    return create_chat(True, chat_name, member_ids, session, user.id)


def get_user_chats(user_id: int, session: Session):
    return session.exec(
        select(Chat).join(target=ChatMember).where(ChatMember.user_id == user_id)
    ).all()


def get_chat_by_id(chat_id: int, session: Session):
    return session.exec(select(Chat).where(Chat.id == chat_id)).one()


def check_user_in_chat(chat_id: int, user_id: int, session: Session):
    session.exec(
        select(ChatMember)
        .where(ChatMember.chat_id == chat_id)
        .where(ChatMember.user_id == user_id)
    ).one()


def transfer_chat_ownership(
    deleter_id: int, chat_id: int, new_owner_id: int, session: Session
) -> None:
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).one()
    if chat.owner_id == deleter_id and new_owner_id in [x.id for x in chat.chatmembers]:
        chat.owner_id = new_owner_id
        return
    raise ValueError("No user with given id in chat")


def update_chat_user_list(
    owner_id: int, chat_id: int, user_id: int, is_to_add: bool, session: Session
):

    def add_user(session: Session, chat_id: int, user_id: int):
        statement = select(ChatMember).where(
            ChatMember.chat_id == chat_id, ChatMember.user_id == user_id
        )
        result = session.exec(statement).first()
        if not result:
            chat_user_link = ChatMember(chat_id=chat_id, user_id=user_id)
            session.add(chat_user_link)
            session.commit()

    def remove_user(session: Session, chat_id: int, user_id: int):
        statement = select(ChatMember).where(
            ChatMember.chat_id == chat_id, ChatMember.user_id == user_id
        )
        result = session.exec(statement).first()
        if result:
            session.delete(result)
            session.commit()

    chat = session.exec(select(Chat).where(Chat.id == chat_id)).one()
    if chat.owner_id == owner_id:
        function = {True: add_user, False: remove_user}
        function[is_to_add](session, chat_id, user_id)
        return
    raise ValueError("User is not chat owner")


def delete_chat(deleter_id: int, chat_id: int, session: Session):
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).one()
    if chat.owner_id == deleter_id:
        session.delete(chat)
        session.commit()
        return
    raise ValueError("User is not chat owner")
