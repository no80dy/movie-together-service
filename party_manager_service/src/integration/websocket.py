import uuid
from collections import defaultdict
from functools import lru_cache

from fastapi import WebSocket


class WebSocketRouter:
    def __init__(self):
        self.connections: dict[uuid.UUID, list[WebSocket]] = defaultdict(list)

    def get_websocket_by_party_id(self, _id: uuid.UUID) -> list[WebSocket]:
        return self.connections[_id]

    def add_connection(self, _id: uuid.UUID, websocket: WebSocket):
        self.connections[_id].append(websocket)

    def remove_connection(self, _id: uuid.UUID, websocket: WebSocket) -> None:
        self.connections[_id].remove(websocket)


@lru_cache(maxsize=1)
def get_stream_websocket_router() -> WebSocketRouter:
    return WebSocketRouter()


@lru_cache(maxsize=1)
def get_chat_websocket_router() -> WebSocketRouter:
    return WebSocketRouter()
