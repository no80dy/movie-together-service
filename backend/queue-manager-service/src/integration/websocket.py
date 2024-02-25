import uuid
from functools import lru_cache

from fastapi import WebSocket


class WebSocketRouteTable:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    def get_websocket_by_ws_id(self, ws_id: str):
        return self.connections[ws_id]

    def add_pair_in_table(self, ws_id: str, websocket: WebSocket):
        self.connections[ws_id] = websocket


@lru_cache(maxsize=1)
def get_websocket_route_table() -> WebSocketRouteTable:
    return WebSocketRouteTable()
