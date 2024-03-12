import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from services.client_id import ClientIDService, get_client_id_service
from services.queue import QueueService, get_queue_service
from services.websocket import WebSocketService, get_websocket_service

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    websocket_service: WebSocketService = Depends(get_websocket_service),
    client_id_service: ClientIDService = Depends(get_client_id_service),
    queue_service: QueueService = Depends(get_queue_service),
):
    film_id = client_id_service.get_film_id_from_client_id(client_id)
    await websocket_service.connect(film_id, websocket)
    await websocket_service.broadcast(film_id, "yeah boy")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_service.broadcast(
                film_id, f"Client #{client_id} says: {data}"
            )
    except WebSocketDisconnect:
        await queue_service.remove_from_queue(film_id, client_id)
        websocket_service.disconnect(film_id, websocket)
        await websocket_service.broadcast(
            film_id, f"Client #{client_id} left the chat"
        )
