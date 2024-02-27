import uuid
import asyncio

from typing import Annotated
from functools import lru_cache
from fastapi import Depends, WebSocket

from integration.websocket import get_websocket_router, WebSocketRouter


class WebSocketConnectionService:
    def __init__(self, websocket_router: WebSocketRouter):
        self.websocket_router = websocket_router

    async def connect(self, user_id: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        self.websocket_router.add_pair_in_table(user_id, websocket)
        # get party_id from mongodb
        while True:
            # Here will be chatting with users
            # Here will be sending a server video playing time
            await asyncio.sleep(1)


@lru_cache
def get_websocket_receiver(
    websocket_router: Annotated[WebSocketRouter, Depends(get_websocket_router)]
) -> WebSocketConnectionService:
    return WebSocketConnectionService(websocket_router)
