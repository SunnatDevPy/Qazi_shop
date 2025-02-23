from fastapi import APIRouter
from starlette.routing import Router
from fastapi import FastAPI, WebSocket

websocket_router = APIRouter(tags=['Websocket'])


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
