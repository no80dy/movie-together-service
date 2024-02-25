import asyncio
import uuid
from functools import lru_cache

from fastapi import Depends, WebSocket

from integration.websocket import WebSocketRouteTable, get_websocket_route_table


class WebSocketService:
    def __init__(
            self,
            websocket_route_table: WebSocketRouteTable,
    ):
        self.websocket_route_table = websocket_route_table

    async def connect(
        self,
        client_id: str,
        websocket: WebSocket
    ) -> None:
        await websocket.accept()
        self.websocket_route_table.add_pair_in_table(client_id, websocket)
        while True:
            await asyncio.sleep(1)


@lru_cache
def get_websocket_service(
    websocket_route_table: WebSocketRouteTable = Depends(get_websocket_route_table)
):
    return WebSocketService(websocket_route_table)
