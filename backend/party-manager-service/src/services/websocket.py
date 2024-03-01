import uuid
import json
import asyncio
import datetime

from typing import Annotated
from functools import lru_cache
from fastapi import Depends, WebSocket, WebSocketDisconnect

from integration.websocket import get_websocket_router, WebSocketRouter
from integration.storages import IStorage, get_storage


class WebSocketConnectionService:
    def __init__(
        self,
        websocket_router: WebSocketRouter,
        storage: IStorage
    ):
        self.websocket_router = websocket_router
        self.storage = storage

    async def connect(
        self, username: str, party_id: uuid.UUID, websocket: WebSocket
    ):
        await websocket.accept()
        self.websocket_router.add_connection(party_id, websocket)
        for websocket_connection in self.websocket_router.get_websocket_by_party_id(party_id):
            await websocket_connection.send_text(
                json.dumps(
                    {"type": "chat", "text": f"{username} joined to the party!"}
                )
            )
        try:
            while True:
                websocket_connections = \
                    self.websocket_router.get_websocket_by_party_id(party_id)
                message = await websocket.receive_text()
                message_json = json.loads(message)
                if message_json["type"] == "chat":
                    for websocket_connection in websocket_connections:
                        await websocket_connection.send_text(
                            json.dumps(
                                {
                                    "type": "chat",
                                    "text": f"{username} says {json.loads(message)['text']}"
                                }
                            )
                        )
                elif message_json["type"] == "pause":
                    for websocket_connection in websocket_connections:
                        await websocket_connection.send_text(
                            json.dumps(
                                {
                                    "type": "pause",
                                }
                            )
                        )
                elif message_json["type"] == "play":
                    for websocket_connection in websocket_connections:
                        await websocket_connection.send_text(
                            json.dumps(
                                {
                                    "type": "play",
                                }
                            )
                        )
                elif message_json["type"] == "seeked":
                    for websocket_connection in websocket_connections:
                        await websocket_connection.send_text(
                            json.dumps(
                                {
                                    "type": "seeked",
                                    "time": message_json["time"]
                                }
                            )
                        )
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            self.websocket_router.remove_connection(party_id, websocket)
            await websocket.send_text(
                json.dumps(
                    {"type": "chat", "text": f"{username} left the party!"}
                )
            )


@lru_cache
def get_websocket_connection_service(
    websocket_router: Annotated[WebSocketRouter, Depends(get_websocket_router)],
    storage: Annotated[IStorage, Depends(get_storage)]
) -> WebSocketConnectionService:
    return WebSocketConnectionService(websocket_router, storage)
