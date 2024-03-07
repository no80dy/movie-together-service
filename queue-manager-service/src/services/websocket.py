import asyncio
import json
import uuid
from functools import lru_cache

from fastapi import Depends, WebSocket
from integration.storages import RedisStorage, get_storage
from integration.websocket import (
    WebSocketRouteTable,
    get_websocket_route_table,
)


class WebSocketService:
    def __init__(
        self,
        storage: RedisStorage,
        websocket_route_table: WebSocketRouteTable,
    ):
        self.storage = storage
        self.websocket_route_table = websocket_route_table

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.websocket_route_table.add_pair_in_table(client_id, websocket)
        # while True:
        #     await asyncio.sleep(1)

    async def reconnect(
        self,
        client_id: str,
    ) -> None:
        """Подключение клиента повторно"""
        # где-то хранить какие фильмы сейчас идут -> Реконект не нужен, смотите заново
        pass

    def disconnect(
        self,
        client_id: str,
    ) -> None:
        self.websocket_route_table.remove_pair_in_table(client_id)
        # TODO удалить из редиса как-то, а как реконнект делать, если вся информация удалится

    async def broadcast(self, film_id: uuid.UUID, message: str):
        """Достает из редиса по айди фильма список юзеров и им рассылает."""
        queue = json.loads(await self.storage.get(str(film_id)))
        client_ids = [user["client_id"] for user in queue["members"]]
        for client_id in client_ids:
            connection = self.websocket_route_table.connections.get(client_id)
            await connection.send_text(message)


@lru_cache
def get_websocket_service(
    storage: RedisStorage = Depends(get_storage),
    websocket_route_table: WebSocketRouteTable = Depends(
        get_websocket_route_table
    ),
):
    return WebSocketService(storage, websocket_route_table)
