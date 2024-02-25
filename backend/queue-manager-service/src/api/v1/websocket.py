from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from services.websocket import WebSocketService, get_websocket_service

from services.websocket import WebSocketService, get_websocket_service

router = APIRouter()


@router.websocket('/ws/{client_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    websocket_service: WebSocketService = Depends(get_websocket_service()),
):
    await websocket_service.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
