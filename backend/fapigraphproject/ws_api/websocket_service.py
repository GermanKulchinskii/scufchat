import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, WebSocket
from sqlmodel import Session

from fapigraphproject import db
from fapigraphproject.methods.authentication_methods import get_current_user
from fapigraphproject.models import Chat, Message

ws_router = APIRouter()

# Глобальное хранилище для активных подключений по chat_id
active_connections = {}


@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, session: Session = Depends(db.get_session)
):
    print("New WebSocket connection attempt")

    # Получаем токен и chat_id из query-параметров
    token = websocket.query_params.get("token")
    chat_id_param = websocket.query_params.get("chat_id")
    print("Token received from query params:", token)
    print("Chat ID received from query params:", chat_id_param)

    if not token or not chat_id_param:
        print("Token или chat_id не предоставлен. Закрываем веб-сокет.")
        await websocket.close(code=1008)
        return

    try:
        chat_id = int(chat_id_param)
    except ValueError:
        print("Некорректный chat_id. Закрываем веб-сокет.")
        await websocket.close(code=1008)
        return

    if token.startswith("Bearer "):
        token = token[7:].strip()
    print("Token after stripping 'Bearer':", token)

    try:
        user = get_current_user(token, session)
        print("User authorized:", user)
    except Exception as e:
        print("Authorization failed:", e)
        await websocket.close(code=1008)
        return

    await websocket.accept()
    print("WebSocket connection accepted.")

    # Регистрируем подключение в глобальном списке для данного чата
    if chat_id not in active_connections:
        active_connections[chat_id] = []
    active_connections[chat_id].append(websocket)

    try:
        async for message in websocket.iter_text():
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            content = data.get("content")
            if content:
                # Отправляем статус отправки отправителю (если необходимо)
                await websocket.send_text(json.dumps({"status": "sending"}))

                # Сохраняем сообщение в базе
                await save_message(content, user.id, chat_id, session)
                print(f"Message from {user.id} in chat {chat_id}: {content}")

                # Формируем время отправки в требуемом формате
                sent_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")

                # Формируем сообщение-подтверждение для отправителя
                confirmation_data = {
                    "chat_id": chat_id,
                    "sender_id": user.id,
                    "content": content,
                    "sentAt": sent_at,
                    "status": "delivered",
                    "type": "confirmation",
                }
                await websocket.send_text(json.dumps(confirmation_data))

                # Формируем сообщение для всех остальных участников чата
                broadcast_data = {
                    "chat_id": chat_id,
                    "sender_id": user.id,
                    "content": content,
                    "sentAt": sent_at,
                    "status": "delivered",
                    "type": "message",
                }
                # Рассылаем сообщение всем подключённым, кроме отправителя
                for connection in active_connections.get(chat_id, []):
                    if connection != websocket:
                        try:
                            await connection.send_text(json.dumps(broadcast_data))
                        except Exception as e:
                            print(f"Error sending message to a connection: {e}")
            else:
                print("Получено сообщение без content")
    except Exception as e:
        print(f"Ошибка обработки сообщений: {e}")
    finally:
        # При отключении удаляем соединение
        if chat_id in active_connections and websocket in active_connections[chat_id]:
            active_connections[chat_id].remove(websocket)
            print(f"WebSocket disconnected from chat {chat_id}")


async def save_message(content: str, sender_id: int, chat_id: int, session: Session):
    chat = session.get(Chat, chat_id)
    if chat:
        message = Message(content=content, sender_id=sender_id, chat=chat)
        session.add(message)
        session.commit()
    else:
        print(f"Chat with id {chat_id} not found")
