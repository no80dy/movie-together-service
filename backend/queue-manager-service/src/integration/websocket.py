import uuid
from functools import lru_cache

from fastapi import WebSocket


class WebSocketRouteTable:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    def get_websocket_by_ws_id(self, client_id: str):
        return self.connections[client_id]

    def add_pair_in_table(self, client_id: str, websocket: WebSocket):
        self.connections[client_id] = websocket

    def remove_pair_in_table(self, client_id: str):
        del self.connections[client_id]


@lru_cache(maxsize=1)
def get_websocket_route_table() -> WebSocketRouteTable:
    return WebSocketRouteTable()
