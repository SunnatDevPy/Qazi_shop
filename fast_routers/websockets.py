from fastapi import APIRouter
from starlette.routing import Router
from fastapi import FastAPI, WebSocket

websocket_router = APIRouter(tags=['Websocket'])

active_connections = set()


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Принимаем подключение
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Ожидаем сообщение от клиента
            print(f"Получено: {data}")
            await send_update_to_clients(f"Обновлённые данные: {data}")  # Рассылаем обновление
    except:
        print("Клиент отключился")
    finally:
        active_connections.remove(websocket)  # Удаляем клиента при отключении


async def send_update_to_clients(message: str):
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except:
            pass  # Пропускаем ошибки отправки (например, если клиент уже отключился)
