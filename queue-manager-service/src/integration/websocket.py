import uuid
from collections import defaultdict
from functools import lru_cache

from fastapi import WebSocket


class WebSocketRouteTable:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    def get_websocket_by_film_id(self, film_id: str) -> list[WebSocket]:
        return self.connections[film_id]

    def add_connection(self, film_id: str, websocket: WebSocket) -> None:
        self.connections[film_id].append(websocket)
        print(self.connections)

    def remove_connection(self, film_id: str, websocket: WebSocket) -> None:
        self.connections[film_id].remove(websocket)


@lru_cache(maxsize=1)
def get_websocket_route_table() -> WebSocketRouteTable:
    return WebSocketRouteTable()
