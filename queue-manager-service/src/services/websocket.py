import asyncio
import json
import logging
import uuid
from functools import lru_cache

from fastapi import Depends, WebSocket
from integration.storages import RedisStorage, get_storage
from integration.websocket import (
    WebSocketRouteTable,
    get_websocket_route_table,
)
from services.client_id import ClientIDService, get_client_id_service


class WebSocketService:
    def __init__(
        self,
        storage: RedisStorage,
        websocket_route_table: WebSocketRouteTable,
        client_id_service: ClientIDService,
    ):
        self.storage = storage
        self.websocket_route_table = websocket_route_table
        self.client_id_service = client_id_service

    async def connect(self, film_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.websocket_route_table.add_connection(film_id, websocket)

    def disconnect(
        self,
        film_id: str,
        websocket: WebSocket,
    ) -> None:
        self.websocket_route_table.remove_connection(film_id, websocket)

    async def broadcast(self, film_id: str, message: str):
        connections = self.websocket_route_table.get_websocket_by_film_id(
            film_id
        )
        for connection in connections:
            try:
                await connection.send_text(message)
            except AttributeError as e:
                logging.error(e)


@lru_cache
def get_websocket_service(
    storage: RedisStorage = Depends(get_storage),
    websocket_route_table: WebSocketRouteTable = Depends(
        get_websocket_route_table
    ),
    client_id_service: ClientIDService = Depends(get_client_id_service),
):
    return WebSocketService(storage, websocket_route_table, client_id_service)
