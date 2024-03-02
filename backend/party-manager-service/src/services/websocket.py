import uuid
import json
import asyncio

from typing import Annotated
from functools import lru_cache
from fastapi import Depends, WebSocket, WebSocketDisconnect

from integration.websocket import get_websocket_router, WebSocketRouter
from integration.storages import IStorage, get_storage
from integration.cache import ICache, get_cache


class WebSocketConnectionService:
    def __init__(
        self,
        websocket_router: WebSocketRouter,
        storage: IStorage,
        cache: ICache
    ):
        self.websocket_router = websocket_router
        self.storage = storage
        self.cache = cache

    async def connect(
        self,
        username: str,
        party_id: uuid.UUID,
        websocket: WebSocket
    ) -> None:
        await websocket.accept()
        self.websocket_router.add_connection(party_id, websocket)
        # await self.notify_all(
        #     party_id,
        #     f"{username} joined to the party!"
        # )
        # if await self.cache.get(party_id):
        data = {
            "type": "timeupdate",
            "time": json.loads((await self.cache.get(party_id)).decode('utf-8'))["time"]
        }
        await websocket.send_text(json.dumps(data))

        try:
            while True:
                message = await websocket.receive_json()
                await self.handle_message(username, party_id, message)
                await self.cache.set(party_id, {"time": message["time"]})
        except WebSocketDisconnect:
            # await self.notify_all(
            #     party_id,
            #     f"{username} left the party!"
            # )
            self.websocket_router.remove_connection(party_id, websocket)
        finally:
            await websocket.close()

    async def notify_all(self, party_id: uuid.UUID, text: str) -> None:
        websocket_connections = \
            self.websocket_router.get_websocket_by_party_id(party_id)
        for websocket_connection in websocket_connections:
            await websocket_connection.send_text(
                json.dumps({"type": "chat", "text": text})
            )

    async def handle_message(
        self,
        username: str,
        party_id: uuid.UUID,
        message: dict
    ) -> None:
        message_type = message["type"]
        websocket_connections = \
            self.websocket_router.get_websocket_by_party_id(party_id)
        # if message_type == "chat":
        #     message_with_user_assign = \
        #         f"{username} says {message['text']}"
        #     await self.send_to_all(
        #         websocket_connections,
        #         {"type": message_type, "text": message_with_user_assign}
        #     )
        if message_type in ["pause", "play"]:
            await self.send_to_all(
                websocket_connections,
                {"type": message_type, "time": message["time"]}
            )
        elif message_type == "seeked":
            await self.send_to_all(
                websocket_connections,
                {"type": message_type, "time": message["time"]}
            )

    async def send_to_all(
        self,
        websocket_connections: list[WebSocket],
        message: dict
    ) -> None:
        for websocket_connection in websocket_connections:
            await websocket_connection.send_json(message)


@lru_cache
def get_websocket_connection_service(
    websocket_router: Annotated[WebSocketRouter, Depends(get_websocket_router)],
    storage: Annotated[IStorage, Depends(get_storage)],
    cache: Annotated[ICache, Depends(get_cache)]
) -> WebSocketConnectionService:
    return WebSocketConnectionService(websocket_router, storage, cache)
