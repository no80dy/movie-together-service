import uuid
import asyncio
import datetime

from typing import Annotated
from functools import lru_cache
from fastapi import Depends, WebSocket

from integration.websocket import get_websocket_router, WebSocketRouter
from integration.storages import IStorage


class WebSocketConnectionService:
    def __init__(
        self,
        websocket_router: WebSocketRouter,
        storage: IStorage
    ):
        self.websocket_router = websocket_router
        self.storage = storage

    async def connect(self, user_id: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        self.storage.find_element_by_properties({""})
        self.websocket_router.add_pair_in_table(user_id, websocket)
        while True:
            result = await self.storage.find_element_by_properties(
                    {"users_ids": {"$in": [user_id]}},
                    "parties"
            )
            played_time = \
                datetime.datetime.utcnow() - datetime.datetime.strptime(
                    result["player_time"], "%Y-%m-%dT%H:%M:%S"
                )
            await websocket.send_json(
                {"type": "sync", "played_time": played_time}
            )
            # Here will be chatting with users
            # Here will be sending a server video playing time
            await asyncio.sleep(1)


@lru_cache
def get_websocket_receiver(
    websocket_router: Annotated[WebSocketRouter, Depends(get_websocket_router)]
) -> WebSocketConnectionService:
    return WebSocketConnectionService(websocket_router)
