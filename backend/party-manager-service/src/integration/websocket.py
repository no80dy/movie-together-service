import uuid

from fastapi import WebSocket
from functools import lru_cache


class WebsocketRouter:
    def __init__(self):
        self.connections: dict[uuid.UUID, WebSocket] = {}

    def get_websocket_by_user_id(self, _id: uuid.UUID) -> WebSocket:
        return self.connections[_id]

    def add_pair_in_table(self, _id: uuid.UUID, websocket: WebSocket):
        self.connections[_id] = websocket


@lru_cache(maxsize=1)
def get_websocket_router() -> WebsocketRouter:
    return WebsocketRouter()
